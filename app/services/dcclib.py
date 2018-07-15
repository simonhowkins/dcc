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
from collections import deque

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

    return [addr, speed_byte]

def idle_instruction():
    return [0xFF, 0]

def stop_instruction(emergency):
    assert emergency == True or emergency == False
    return [0, 0x50 + emergency]

# Calculate the checksum of the supplied list of values
def checksum(values):
    return functools.reduce(lambda a, b: a ^ b, values)

# Append a checksum to the supplied list of values
def add_checksum(values):
    return values + [checksum(values)]

# Convert a packet of one or more bytes into a DCC stream of bits
def to_stream(command):
    command = add_checksum(command)
    command = flatten([[0] + to_binary_array(b) for b in command])
    return flatten([
        [1] * 13,
        command,
        [1],
    ])

# Flatten a list of lists, shallowly
# [[1,2,3],[4,5,6]]      -> [1,2,3,4,5,6]
# [[1,[2,3]], [[4,5],6]] -> [1,[2,3],[4,5],6]
def flatten(values):
    return functools.reduce(lambda a, b: a + b, values, [])

# Turn a value (0..255) into a list of 8 bits
def to_binary_array(value8):
    if not isinstance(value8, (list, tuple)):
        value8 = [value8]
    result = [(v >> bit) & 1 for v in value8 for bit in range(7, -1, -1)]
    return result

# Convert a stream of bits into a digital DCC waveform
def to_signal(stream):
    return flatten([[1, 0] if b else [1, 1, 0, 0] for b in stream])

def round_up(signal):
    assert len(signal) % 4 == 0
    signal = signal + [1,1,0,0] * (((32 - len(signal)) % 32) >> 2)
    assert len(signal) % 32 == 0
    return signal

# Turn a list of 8 bits into a value (0..255)
def to_byte(bits):
    assert len(bits) == 8
    return functools.reduce(lambda total, bit: (total << 1) + bit, bits, 0)

# Turn a list of 8 * N bits into a list of N values
def to_bytes(bits):
    return [to_byte(bits[i:i + 8]) for i in range(0, len(bits), 8)]

def decode_signal(signal):
    stream = []
    pos = 0
    while pos < len(signal):
        bitbit = (signal[pos] << 1) + signal[pos+1]
        assert bitbit in [3,2]
        if bitbit == 2:
            stream += [1]
        elif bitbit == 3:
            pos += 2
            bitbit = (signal[pos] << 1) + signal[pos+1]
            assert bitbit == 0
            stream += [0]
        pos += 2
    return stream

def decode_stream(stream):
    result = []
    pos = 0
    while stream[pos] == 1:
        pos += 1
    assert pos > 12
    while stream[pos] == 0:
        result += [to_byte(stream[pos+1:pos+9])]
        pos += 9
    assert len(result) >= 2
    check = result[-1]
    result.pop()
    assert checksum(result) == check
    return result

def decode_instruction(instruction):
    instruction = deque(instruction)
    address = instruction.popleft()
    if address == 0xFF and instruction[0] == 0:
        return (address, "IDLE", ())
    elif address == 0x00 and (instruction[0] & 0x50) == 0x50:
        return (address, "STOP", (instruction[0] & 1,))
    elif (instruction[0] & 0xA0) == 0x20:
        forwards = (instruction[0] & 0x40) == 0x40
        speed = ((instruction[0] & 0x0F) << 1) + ((instruction[0] & 0x10) >> 4)
        if speed > 0:
            speed -= 3
        return (address, "SPEED", (forwards, speed))
    assert False, "Failed to decode instruction"

def unit_test():
    assert to_stream([1, 2]) == [1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,1,1]
    assert to_binary_array(0) == [0,0,0,0,0,0,0,0]
    assert to_binary_array(255) == [1,1,1,1,1,1,1,1]
    assert to_binary_array([0, 255]) == [0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1]
    assert to_binary_array(0xA) == [0,0,0,0,1,0,1,0]
    assert to_signal([1, 0]) == [1, 0, 1, 1, 0, 0]
    assert add_checksum([45, 45]) == [45, 45, 0]
    assert checksum([1, 2, 2, 4, 8, 8]) == 5
    assert to_byte([0, 0, 0, 0, 1, 0, 1, 0]) == 10
    for i in range(0, 255):
        assert i == to_byte(to_binary_array(i))
    assert to_bytes([0,0,0,0,1,1,1,1]) == [15]
    assert to_bytes([0,0,0,0,1,1,1,1, 0,0,0,0,1,0,1,0]) == [15, 10]
    stop_instruction(True)
    stop_instruction(False)
    assert round_up([]) == []
    assert round_up([1,1,1,1]) == [1,1,1,1,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0]
    assert round_up([1,1,1,1,0,0,0,0]) == [1,1,1,1,0,0,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0]
    longest = 0
    for addr in range(1, 32):
        for speed in range(0, 28):
            for direction in [True, False]:
                sig = to_bytes(round_up(to_signal(to_stream(speed_instruction(addr, direction, speed)))))
                l = len(sig)
                longest = max(longest, l)
#    print(longest)
    assert decode_signal([1,0,1,0,1,1,0,0,1,0]) == [1,1,0,1]
    assert decode_stream([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,0,0,0,0,0,1,0,1,0,0,1,1,1,1,0,1,0,1,1]) == [255,10]

    for addr in range(1, 31):
        for speed in range(0, 28):
            for direction in [True, False]:
                assert decode_instruction(decode_stream(decode_signal(to_binary_array(to_bytes(round_up(to_signal(to_stream(speed_instruction(addr, direction, speed))))))))) == (addr, "SPEED", (direction, speed))
