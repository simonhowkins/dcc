# DCC - Digital Command Control command station
# Copyright (C) 2018 Simon Howkins
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Source for this program is published at https://github.com/simonhowkins/dcc

import atexit

from apscheduler.schedulers.background import BackgroundScheduler

from app.services import dcclib
from app.models.dma_buffer import DmaBuffer

"""DCC Channel model

Ie an encapsulation of a DCC address and the activity occurring on that
channel"""

DmaBuffer.unit_test()

class DccChannel(object):
    # Class constants:
    FORWARDS  = 1
    BACKWARDS = -1

    MAX_ADDR = 30
    assert MAX_ADDR < 127
    BYTES_PER_CHANNEL = 16

    # Class attributes:
    # The singleton status of *all* channels
    _channels = [{
        "throttle": 0,
        "speedAdjusterJob": None,
    }] * MAX_ADDR
    # The array starts at index 0 (duh) which is not a drivable channel,
    # but it can be safely ignored

    run_buffer = DmaBuffer(MAX_ADDR * BYTES_PER_CHANNEL, 0)

    scheduler = BackgroundScheduler()
    scheduler.start()

    atexit.register(lambda: DccChannel.scheduler.shutdown(wait=False))

    def peek_instruction(buf, fromAddr):
        offset = fromAddr * DccChannel.BYTES_PER_CHANNEL
        instBytes = buf[offset:offset + DccChannel.BYTES_PER_CHANNEL]
        (instAddr, instType, (direction, speed)) = dcclib.decode_instruction(dcclib.decode_stream(dcclib.decode_signal(dcclib.to_binary_array(instBytes))))
        assert instAddr == fromAddr
        assert instType == "SPEED"
        assert direction in [True, False]
        assert speed >= 0
        assert speed <= 28
        return (direction, speed)

    def poke_instruction(buf, addr, instruction):
        offset = addr * DccChannel.BYTES_PER_CHANNEL
        bytes_to_poke = dcclib.to_bytes(dcclib.round_up(dcclib.to_signal(dcclib.to_stream(instruction))))
        assert len(bytes_to_poke) <= DccChannel.BYTES_PER_CHANNEL
        buf[offset:offset + len(bytes_to_poke)] = bytes_to_poke

    def __init__(self, addr):
        # Instance attributes:
        self._addr = int(addr)
        assert self._valid()

    def __repr__(self):
        return "DccChannel[addr=%s,%d%s]" % (self.addr, self.speed, ">" if self.direction == DccChannel.FORWARDS else "<")

    def _valid(self):
        assert self._addr > 0
        assert self._addr <= DccChannel.MAX_ADDR
        assert self._channels[self._addr]["throttle"] >= 0
        assert self._channels[self._addr]["throttle"] <= 28
        return True

    @property
    def addr(self):
        assert self._valid()
        return self._addr

    @property
    def direction(self):
        assert self._valid()
        (direction, speed) = DccChannel.peek_instruction(DccChannel.run_buffer, self._addr)
        return DccChannel.FORWARDS if direction else DccChannel.BACKWARDS

    @direction.setter
    def direction(self, direction):
        assert self._valid()
        assert direction in [DccChannel.FORWARDS, DccChannel.BACKWARDS], str(direction)
        (prevDirection, speed) = DccChannel.peek_instruction(DccChannel.run_buffer, self._addr)
        if (speed == 0):
            DccChannel.poke_instruction(DccChannel.run_buffer, self._addr, dcclib.speed_instruction(self._addr, direction == DccChannel.FORWARDS, 0))

    @property
    def speed(self):
        assert self._valid()
        (direction, speed) = DccChannel.peek_instruction(DccChannel.run_buffer, self._addr)
        return speed

    @speed.setter
    def speed(self, speed):
        assert self._valid()
        assert speed >= 0
        assert speed <= 28
        (direction, prevSpeed) = DccChannel.peek_instruction(DccChannel.run_buffer, self._addr)
        DccChannel.poke_instruction(DccChannel.run_buffer, self._addr, dcclib.speed_instruction(self._addr, direction, speed))

    def _setSpeed(self, speed):
        (direction, prevSpeed) = DccChannel.peek_instruction(DccChannel.run_buffer, self._addr)
        DccChannel.poke_instruction(DccChannel.run_buffer, self._addr, dcclib.speed_instruction(self._addr, direction, speed))

    @property
    def throttle(self):
        assert self._valid()
        return self._channels[self._addr]["throttle"]

    @throttle.setter
    def throttle(self, throttle):
        assert self._valid()
        assert throttle >= 0
        assert throttle <= 28
        self._channels[self._addr]["throttle"] = throttle
        self._setSpeedAdjuster(throttle)

    def _clearSpeedAdjuster(self):
        if self._channels[self._addr]["speedAdjusterJob"] != None:
            self._channels[self._addr]["speedAdjusterJob"].remove()
            self._channels[self._addr]["speedAdjusterJob"] = None

    def _setSpeedAdjuster(self, destinationSpeed):
        # How does the required speed compare to the current speed...
        currentSpeed = self.speed

        # If going at the right speed, remove the speedAdjuster, job done
        if currentSpeed == destinationSpeed:
            self._clearSpeedAdjuster()
            return

        # Work out how to adjust the speed, if at all
        adjustment = 0
        if currentSpeed < destinationSpeed:
            # We need to accelerate
            adjustment = 1
        elif currentSpeed > destinationSpeed:
            # We need to brake
            adjustment = -1

        def doIt():
            currentSpeed = self.speed
            # Work out how to adjust the speed, if at all
            adjustment = 0
            if currentSpeed < destinationSpeed:
                adjustment = 1
            elif currentSpeed > destinationSpeed:
                adjustment = -1
            # If speed needs adjusting, adjust it
            if adjustment != 0:
                currentSpeed = currentSpeed + adjustment
                self.speed = currentSpeed
            # If now going at the right speed, remove the speedAdjuster
            if currentSpeed == destinationSpeed:
                self._clearSpeedAdjuster()

        self._clearSpeedAdjuster()
        self._channels[self._addr]["speedAdjusterJob"] = self.scheduler.add_job(doIt, "interval", seconds=0.2)

def unit_test():
    assert DccChannel(1).addr == 1
    assert DccChannel(2).addr == 2
    a = DccChannel(5)
    assert a.speed == 0
    a.direction = DccChannel.BACKWARDS
    assert a.direction == DccChannel.BACKWARDS
    a.speed = 10
    assert a.speed == 10
    a.throttle = 20
    assert a.throttle == 20
    b = DccChannel(5)
    assert a.addr == b.addr
    assert a.speed == b.speed
    assert a.direction == b.direction
    assert a.throttle == b.throttle
    a.speed = 0
    a.throttle = 0
    a.direction = DccChannel.FORWARDS

DccChannel.poke_instruction(DccChannel.run_buffer, 0, dcclib.idle_instruction())
for addr in range(1, DccChannel.MAX_ADDR):
    DccChannel.poke_instruction(DccChannel.run_buffer, addr, dcclib.speed_instruction(addr, True, 0))

