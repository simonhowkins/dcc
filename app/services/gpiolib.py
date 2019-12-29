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

"""GPIO functions
"""

import app.services.memlib as memlib

registers = None

def _init():
    print("Initialising gpiolib")
    global registers
    registers = memlib.physicalToVirtual(0x3F200000, 0x100)

# Get the function allocated to a GPIO
def getFunction(gpio):
    assert gpio >= 0
    assert gpio <= 53
    register = 0x00 + (gpio // 10 * 4)
    bit = (gpio % 10) * 3
    regval = memlib.peek(registers, register)
    regval = regval >> bit
    function = regval & 0x7
    functionNames = ["r", "w", "a5", "a4", "a0", "a1", "a2", "a3"] # Sic
    return functionNames[function]

# Set the function allocated to a GPIO
def setFunction(gpio, function):
    function = function.lower()
    assert gpio >= 0
    assert gpio <= 53
    assert function in ["r", "w", "a0", "a1", "a2", "a3", "a4", "a5"]
    function = {
        "r" : 0,
        "w" : 1,
        "a0": 4,
        "a1": 5,
        "a2": 6,
        "a3": 7,
        "a4": 3,
        "a5": 2,
    }[function]
    register = gpio // 10 * 4
    shift = (gpio % 10) * 3
    regval = memlib.peek(registers, register)
    regval = regval & ~(       7 << shift)
    regval = regval |  (function << shift)
    memlib.poke(registers, register, regval)

# Returns the value of a GPIO input - 0 or 1
def read(gpio):
    assert gpio >= 0
    assert gpio <= 53
    register = 0x34 + (gpio // 32) * 4
    shift = gpio % 32
    regval = memlib.peek(registers, register)
    return (regval >> shift) & 1

# Sets the value of a GPIO output - 0 or 1
def write(gpio, value):
    assert gpio >= 0
    assert gpio <= 53
    assert value in [0, 1]
    if value == 0:
        # Write to the CLEAR register
        regBase = 0x28
    else:
        # Write to the SET register
        regBase = 0x1C
    register = regBase + (gpio // 32) * 4
    shift = gpio % 32
    memlib.poke(registers, register, 1 << shift)

def unit_test():
    print("unit testing gpiolib")
    setFunction(18, "r")
    setFunction(18, "R")
    setFunction(18, "w")
    setFunction(18, "W")
    setFunction(18, "a0")
    setFunction(18, "A0")
    setFunction(18, "A1")
    setFunction(18, "A2")
    setFunction(18, "A3")
    setFunction(18, "A4")
    setFunction(18, "A5")

    for (gpio, function) in [
        (-1, "r"),
        (54, "r"),
        ("0", "r"),
        ("A", "r"),
        (18, ""),
        (18, "Q"),
        (18, "q"),
        (18, "a"),
        (18, "a6"),
        (18, "a0 "),
    ]:
        exceptionThrown = False
        try:
            setFunction(gpio, function)
        except:
            exceptionThrown = True
        assert exceptionThrown, "No exception thrown when calling setFunction({}, {})".format(repr(gpio), repr(function))

    assert read(0) in [0, 1]
    assert read(1) in [0, 1]
    assert read(18) in [0, 1]
    assert read(19) in [0, 1]
    assert read(53) in [0, 1]

    for gpio in [-1, 54, "booblyboo"]:
        exceptionThrown = False
        try:
            read(gpio)
        except:
            exceptionThrown = True
        assert exceptionThrown, "No exception thrown when calling read({})".format(repr(gpio))

    write(18, 0)
    write(18, 1)
    write(19, 0)
    write(19, 1)

    for (gpio, value) in [
        (-1, 0),
        (54, 1),
        ("?", 1),
        (19, 2),
        (19, -1),
    ]:
        exceptionThrown = False
        try:
            write(gpio, value)
        except:
            exceptionThrown = True
        assert exceptionThrown, "No exception thrown when calling write({}, {})".format(repr(gpio), repr(value))

    setFunction(18, "W")
    setFunction(19, "W")
    write(18, 0)
    assert read(18) == 0
    write(18, 1)
    assert read(18) == 1
    write(19, 0)
    assert read(18) == 1
    assert read(19) == 0
    write(18, 0)
    write(19, 1)
    assert read(18) == 0
    assert read(19) == 1

    print("gpiolib unit tests complete")

_init()
unit_test()
