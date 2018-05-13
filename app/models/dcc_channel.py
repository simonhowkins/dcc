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

"""DCC Channel model

Ie an encapsulation of a DCC address and the activity occurring on that
channel"""

class DccChannel(object):
    # Class constants:
    FORWARDS  = 1
    BACKWARDS = -1

    MAX_ADDR = 126
    assert MAX_ADDR < 127

    # Class attributes:
    # The singleton status of *all* channels
    _channels = [{
        "direction": 1, # Ie, FORWARDS, except Python 3 blocks that
        "speed": 0,
        "throttle": 0,
    } for a in range(1, MAX_ADDR)]

    def __init__(self, addr):
        # Instance attributes:
        self._addr = int(addr)
        assert self._valid()

    def __repr__(self):
        return "DccChannel[addr=%s,%d%s]" % (self.addr, self.speed, ">" if self.direction == DccChannel.FORWARDS else "<")

    def _valid(self):
        assert self._addr > 0
        assert self._addr <= DccChannel.MAX_ADDR
        assert self._channels[self._addr]["direction"] in [DccChannel.FORWARDS, DccChannel.BACKWARDS]
        assert self._channels[self._addr]["speed"] >= 0
        assert self._channels[self._addr]["speed"] <= 28
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
        return self._channels[self._addr]["direction"]

    @direction.setter
    def direction(self, direction):
        assert self._valid()
        assert direction in [DccChannel.FORWARDS, DccChannel.BACKWARDS], str(direction)
        if (self._channels[self._addr]["speed"] == 0):
            self._channels[self._addr]["direction"] = direction

    @property
    def speed(self):
        assert self._valid()
        return self._channels[self._addr]["speed"]

    @speed.setter
    def speed(self, speed):
        assert self._valid()
        assert speed >= 0
        assert speed <= 28
        self._channels[self._addr]["speed"] = speed

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
        self._channels[self._addr]["speed"] = throttle

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

