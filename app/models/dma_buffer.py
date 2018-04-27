"""DMA buffer model

A block of memory that can be streamed by DMA"""

from ctypes import *

c_ubyte_p = POINTER(c_ubyte)

# Returns the address rounded up (if necessary) to match the alignment
# alignment is assumed to be a power of 2
def _aligned(address, alignment):
    return (address + alignment - 1) & ~(alignment - 1)

class DmaBuffer:

    def __init__(self, size, dest):
        assert size & 31 == 0, "DMA buffer must be a multiple of 32 bytes"
        # Instance attributes:
        self.size = size
        self.memory = (c_ubyte * (32 + 32 + size))()
        aligned_address = _aligned(addressof(self.memory), 32)
        self.header = (c_uint32 * 8).from_address(aligned_address)
        self.buffer = (c_ubyte * size).from_address(aligned_address + 32)

        # Set up DMA control block
        self.header[0:8] = [
            0x00050148,           # Transfer info
            aligned_address + 32, # Data source (self.buffer)
            dest,                 # Data destination
            size,                 # Amount of data
            0,                    # Stride (N/A)
            0,                    # Next block (none yet)
            0,                    # Reserved
            0,                    # Reserved
        ]
        assert self._valid()

    def set_next_buffer(self, next_buffer):
        assert self.valid()
        assert next_buffer
        assert next_buffer.valid()
        self.header[5] = addressof(next_buffer.header)

    # Peek method - ie a = dmaBuffer[5] or a = dmaBuffer[4:7]
    def __getitem__(self, index):
        assert self._valid()
        return self.buffer[index]

    # Poke method - ie dmaBuffer[5] = 10 or dmaBuffer[4:7] = [10, 11, 12]
    def __setitem__(self, index, value):
        assert self._valid()
        self.buffer[index] = value

    def __repr__(self):
        return "DmaBuffer[size=%d]" % (self.size)

    def _valid(self):
        assert self.size > 0
        assert self.memory
        assert self.header
        assert self.buffer
        return True

    @staticmethod
    def unit_test():
        print "unit testing DmaBuffer"
        buffer1 = DmaBuffer(128, 0)
        buffer1.buffer[18] = 45
        assert buffer1[18] == 45
        buffer1.buffer[0:4] = [1,2,3,4]
        assert buffer1[0] == 1
        assert buffer1[1:3] == [2,3]
        buffer1[4:8] = buffer1[0:4]
        assert buffer1[7] == 4

