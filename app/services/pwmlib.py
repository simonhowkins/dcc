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

"""PWM functions

Functions to set up the PWM HW
"""

import sys

import app.services.memlib as memlib
import app.services.gpiolib as gpiolib

pwm = None
timers = None

# Where's the PWM clock amongst the timers registers
pwmTimerOffset = 0xA0
# Actually, try the PCM clock
pwmTimerOffset = 0x98

def _init():
    print("Initialising pwmlib")
    # Map in the PWM registers
    global pwm
    pwm = memlib.physicalToVirtual(0x3F20C000, 0x00000028)
    # Map in some timer registers
    global timers
    timers = memlib.physicalToVirtual(0x3F101000, 0x200)

def reset():
    """Completely reset both PWM channels"""
#    assert channel >= 0
#    assert channel <= 1

    # Stop PWM, clear FIFO
    memlib.poke(pwm, 0x00, 0x40)
    # Clear any error state
    memlib.poke(pwm, 0x04, 0x1FFF)

    print("Initial PWM clock setup = 0x{:08x}, 0x{:08x}".format(
        memlib.peek(timers, pwmTimerOffset + 0),
        memlib.peek(timers, pwmTimerOffset + 4),
    ))

    # Stop clock
    regval = memlib.peek(timers, pwmTimerOffset + 0)
    memlib.poke(timers, pwmTimerOffset + 0, 0x5A000000 | (regval & ~0x10))
    # Wait for it to stop
    while memlib.peek(timers, pwmTimerOffset + 0) & 0x80: pass

def configure(usec):
    """Set up PWM timing for specified pulse length (microseconds)"""
    assert usec >=1
    assert usec == 58

    # Set up GPIO to output our PWM signal
#    gpiolib.setFunction(18, "a5")
#    gpiolib.setFunction(19, "a5")
    gpiolib.setFunction(4, "r")

    # Set clock divisor to set clock pulse duration to 58us
    # Pulses that are 58us high and 58us low means a 8620.69 Hz square wave
    # 58us = 0.000058s
    # 2 * 58us = 0.000116s
    # 1/0.000116s = 8620.69/s (Units /s == Hz)
    # The oscillator runs at 19.2MHz = 19200000 Hz
    # We'd like the clock to tick every 58us, which is (1 / 0.000058) Hz = 17241 Hz
    # So we need the clock to tick every (19200000 / 17241 = 1113.6) ticks of the oscillator
    # The clock divisor register takes a fixed point number, with 12 fractional bits
    # int() discards any fractional value, so to get rounding to the nearest whole number we add 0.5
    # 1113.6 * (1 << 12) + 0.5 = 0x45999A
    divisor = int(19200000 * usec / 1000000 * (1 << 12) + 0.5)
    assert divisor >= (1 << 12)
    assert divisor < (1 << 24)
##    print("PWM clock divisor = 0x{:08x}".format(divisor))
    memlib.poke(timers, pwmTimerOffset + 4, 0x5A000000 + divisor)

    # Set oscillator as clock source
##    print("Set PWM clock source")
    memlib.poke(timers, pwmTimerOffset + 0, 0x5A000000 | 0x01)

    # Wait for it to deal with that
    while memlib.peek(timers, pwmTimerOffset + 0) & 0x80: pass

    # Start PWM clock
##    print("Start PWM clock")
    memlib.poke(timers, pwmTimerOffset + 0, 0x5A000000 | 0x11)

    print("PWM clock (0x{:08X}) setup = 0x{:08X}, 0x{:08X}".format(
        pwmTimerOffset,
        memlib.peek(timers, pwmTimerOffset + 0),
        memlib.peek(timers, pwmTimerOffset + 4),
    ))

    debug("1")

#    sys.stdin.readline()
    # Set PWM DMA config
##    memlib.poke(pwm, 0x08, 0x80000707)
    memlib.poke(pwm, 0x08, 0x0707)

    debug("2")

    delay(3)

    # Set PWM range
    memlib.poke(pwm, 0x10, 32)
#    memlib.poke(pwm, 0x20, 32)

    delay(3)

    debug("3")
    # DEBUG - Set PWM data
    memlib.poke(pwm, 0x14, 0xAAAAAAAA)
#    memlib.poke(pwm, 0x24, 0xFFFFFFFF)

    memlib.poke(pwm, 0x18, 0xFFFFFFFF)

    debug("4")

    debug("Nearly...")
    delay(3)

    memlib.poke(pwm, 0x04, 0x100)
    delay(1)

    # Set PWM state
    memlib.poke(pwm, 0x00, 0x0F00)
#    memlib.poke(pwm, 0x00, 0x23)
#    memlib.poke(pwm, 0x00, 0x2700)

    delay(1)
    memlib.poke(pwm, 0x04, 0x100)
    delay(1)
    debug("End")
    gpiolib.dump()
    print(gpiolib.getFunction(4))

def pwm_terminate():
    # Restore audio PWM (and clear FIFO too)
#    p%!0 = p%!0 OR &40
#    p%!0 = p%!0 AND NOT 1
    # Turn the audio DMA back on

    # Restore GPIO to default state
    gpiolib.write(18, 0)
    gpiolib.setFunction(18, "w")

def debug(q=""):
    print(q)
    for i in range(0x00, 0x28, 4):
        print("PWM reg 0x{:02X} = 0x{:08X}".format(i, memlib.peek(pwm, i)))

def delay(d):
    print("." * d)
    for i in range(d * 1000000):
        pass
    
def unit_test():
    print("unit testing pwmlib")
    reset()
    configure(58)
    print("pwmlib unit tests complete")

_init()
unit_test()
