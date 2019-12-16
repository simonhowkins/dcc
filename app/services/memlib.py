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

"""Memory functions
"""

import os
import struct
import mmap

from ctypes import *
import ctypes.util

kernel = CDLL(ctypes.util.find_library("c"))
pageSize = os.sysconf("SC_PAGE_SIZE")
memfd = None

def _init():
    print("Initialising memlib")
    global memfd
    try:
        memfd = os.open("/dev/mem", os.O_RDWR)
    except PermissionError:
        # TODO: Is there some sensible fallback so someone could work on
        # the front-end without having to have root access, or a Pi at all?!
        raise Exception("Cannot access pysical memory - not running as root?")

def physicalToVirtual(physical, count):
    if (physical & (mmap.ALLOCATIONGRANULARITY - 1)):
        raise Exception("Cannot map un-aligned physical address 0x{:x}; granularity is 0x{:x}".format(physical, mmap.ALLOCATIONGRANULARITY))
    virtual = mmap.mmap(memfd, count, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE, offset=physical)
    if virtual == -1:
        raise Exception("Could not map physical address 0x{:x}, errno = {}".format(physical, ctypes.get_errno()))
    return virtual

def virtualToPhysical(virtual):
    pageNumber = int(virtual / pageSize)
    pageOffset = virtual % pageSize
    filename = "/proc/self/pagemap"
    offset = pageNumber * 8
    with open(filename, 'rb') as f:
        f.seek(offset, 0)
        pageInfo = f.read(8)
    # Convert the bytes into a 64 bit number
    pageInfo = struct.unpack('Q', pageInfo)[0]
    # Bottom 55 bits of pageInfo is physical page number
    mask = (1 << 55) - 1
    pageNumber = pageInfo & mask
    return pageNumber * pageSize + pageOffset

def physicalToBus(physical):
    # This will only work with RAM addresses for now
    assert (physical & 0xC0000000) == 0
    return physical | 0xC0000000

def lock(addr, count):
    kernel.mlock(addr, count)
    # TODO: Do we also need to do something so that the kernel won't change the
    # physical address for this virtual address?

# Word read
def peek(buffer, offset):
    assert offset & 0x3 == 0
    return struct.unpack_from("<L", buffer, offset)[0]
# Word write
def poke(buffer, offset, value):
    assert offset & 0x3 == 0
    struct.pack_into("<L", buffer, offset, value)

def unit_test():
    print("Unit testing memlib")
    registers = physicalToVirtual(0x3F000000, 0x00010000)
    print("Registers mapped at ", registers)

    # Allocate some memory
    count = mmap.ALLOCATIONGRANULARITY
    memory = (c_ubyte * count * 2)()
    # Get an aligned pointer within the block
    memory = (c_ubyte * count).from_address(addressof(memory) & ~(mmap.ALLOCATIONGRANULARITY - 1))
    print("Using virt addr {}".format(hex(addressof(memory))))
    memory[0:4] = b"1234"
    # Locate the physical address of the memory being used
    physAddr = virtualToPhysical(addressof(memory))
    physAddr = physAddr & ~(mmap.ALLOCATIONGRANULARITY - 1)
    print("Physical address is: ", hex(physAddr))
    # Map in that physical address
    moreMemory = physicalToVirtual(physAddr, count)
    assert moreMemory[0:4] == b'1234'
    print("memlib unit tests complete")

_init()
unit_test()

