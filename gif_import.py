from lzw_gif import *


# test case 2
decompressed_data = [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 3, 3, 1, 3, 3, 2, 3, 3, 2, 1, 3, 3, 2, 3, 3, 2, 3, 3, 2, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 1, 0, 0, 3, 3, 1, 3, 2, 0, 2, 2, 2, 0, 3, 1, 1, 0, 2, 1, 1, 2, 2, 0, 1, 1, 0, 0, 2, 1, 1, 2, 3, 1, 1, 3, 3, 3, 2, 3, 1, 2, 1, 1, 2, 3, 3, 3, 2, 3, 1, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1]
compressed_data1 = [0x02,0x20,0x8C,0x23,0xA9,0x31,0xC3,0x23,0x9A,0x78,0x11,0xCA,0x73,0xD4,0x04,0xA0,0x31,0x01,0x28,0x9D,0x11,0x1A,0x09,0x40,0x96,0x88,0xF3,0x58,0x88,0xD9,0xB8,0xDA,0x84,0x15,0x00]
lzw_min_code_size = compressed_data[0]
compressed_data2 = compress(decompressed_data, lzw_min_code_size)
print(compressed_data2)

hex1 = [hex(i) for i in compressed_data1]
hex2 = [hex(i) for i in compressed_data2]
print(hex1)
print(hex2)
print(hex1 == hex2)


