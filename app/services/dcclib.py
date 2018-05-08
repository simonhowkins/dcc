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

"""DCC functions

Eg:
* Building DCC commands/instructions (sequences of bytes)
* Encoding commands as packets (sequences of bits)
* Encoding packets as bit streams (also sequences of bits)
* Packing bit streams into sequences of bytes to put in memory to be transmitted

And the reverse of the above
"""

import functools

# Build a speed instruction
def speed_instruction(addr, forwards, speed):
    assert addr > 0
#    assert addr < 100
    assert forwards == True or forwards == False
    assert speed >= 0
    assert speed <= 28
    speed_byte = 0x20
    if forwards:
        speed_byte += 0x40
    # Avoid the special Emergency Stop values
    if speed != 0:
        speed += 3
    # Speed bits
    speed_byte += (speed & 1) << 4
    speed_byte += (speed >> 1)

    return add_checksum([addr, speed_byte])

def idle_instruction():
    return add_checksum([0xFF, 0])

def stop_instruction(emergency):
    assert emergency == True or emergency == False
    return add_checksum([0, 0x50 + emergency])

def checksum(values):
    return functools.reduce(lambda a, b: a ^ b, values)

def add_checksum(values):
    return values + [checksum(values)]

# Convert a packet of one or more bytes into a DCC stream of bits
def to_stream(command):
    command = flatten([[0] + to_binary_array(b) for b in command])
    return flatten([
        [1] * 14,
        command,
        [1],
    ])

# Flatten a list of lists, shallowly
# [[1,2,3],[4,5,6]]      -> [1,2,3,4,5,6]
# [[1,[2,3]], [[4,5],6]] -> [1,[2,3],[4,5],6]
def flatten(values):
    return functools.reduce(lambda a, b: a + b, values, [])

def to_binary_array(value8):
    if not isinstance(value8, (list, tuple)):
        value8 = [value8]
    result = [(v >> bit) & 1 for v in value8 for bit in range(7, -1, -1)]
    return result

# Convert a stream of bits into a digital DCC waveform
def to_signal(stream):
    return flatten([[1, 0] if b else [1, 1, 0, 0] for b in stream])

def round_up(signal):
    assert len(signal) % 2 == 0

def to_byte(bits):
    assert len(bits) == 8
    result = 0
#    reduce()

def to_bytes(bits):
    return [to_byte(bits[i:i + 8]) for i in xrange(0, len(bits), 8)]

def unit_test():
    assert to_stream([1, 2]) == [1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,1]
    assert to_binary_array(0) == [0,0,0,0,0,0,0,0]
    assert to_binary_array(255) == [1,1,1,1,1,1,1,1]
    assert to_binary_array([0, 255]) == [0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1]
    assert to_binary_array(0xA) == [0,0,0,0,1,0,1,0]
    assert to_signal([1, 0]) == [1, 0, 1, 1, 0, 0]
    assert add_checksum([45, 45]) == [45, 45, 0]
    assert checksum([1, 2, 2, 4, 8, 8]) == 5
    stop_instruction(True)
    stop_instruction(False)
    longest = 0
    for addr in range(1, 127):
        for speed in range(0, 28):
            for direction in [True, False]:
                l = len(to_signal(to_stream(speed_instruction(addr, direction, speed))))
#                print(l)
                longest = max(longest, l)
    print(longest)
