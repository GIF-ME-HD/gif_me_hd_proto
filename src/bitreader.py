import struct

class BitReader:
    def __init__(self, data, offset=0):
        self.bytez = data
        self.memview = memoryview(self.bytez)
        self.length = len(self.bytez)
        self.byte_offset = offset
        self.bit_offset = 0

    def read_n_bits(self, num_bits):
        ret = 0
        read_bits_so_far = 0
        remainder_bits_current_byte = 8-self.bit_offset
        if num_bits >= remainder_bits_current_byte:
            mask = (1 << remainder_bits_current_byte) - 1
            mask <<= self.bit_offset
            to_app = self.bytez[self.byte_offset] & mask
            to_app >>= self.bit_offset
            ret |= to_app << read_bits_so_far
            self.bit_offset += remainder_bits_current_byte
            num_bits -= remainder_bits_current_byte
            read_bits_so_far += remainder_bits_current_byte
            if self.bit_offset == 8:
                self.byte_offset += 1
                self.bit_offset = 0

        while num_bits > 8:
            ret |= self.bytez[self.byte_offset] << read_bits_so_far
            self.byte_offset += 1
            num_bits -= 8
            read_bits_so_far += 8

        remainder_bits_current_byte = 8-self.bit_offset
        if num_bits > 0 and num_bits <= remainder_bits_current_byte:
            mask = (1 << num_bits) - 1
            mask <<= self.bit_offset
            to_app = self.bytez[self.byte_offset] & mask
            to_app >>= self.bit_offset
            ret |= to_app << read_bits_so_far
            self.bit_offset += num_bits
            if self.bit_offset == 8:
                self.byte_offset += 1
                self.bit_offset = 0
        return ret

if __name__ == '__main__':
    a = BitReader(b"ab")
    print(bin(a.read_n_bits(8)))
    print(bin(a.read_n_bits(8)))