import lzw_gif_cpp

import sys
sys.path.append(r"../")

import lzw_gif3

lzw_min_code_size = 2
input_indices = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 1,
                     0, 0, 0, 0, 2, 2, 2, 1, 1, 1, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 0, 0, 0,
                     0, 1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 1, 1,
                     1]
my_compressed_data = lzw_gif_cpp.compress(input_indices, lzw_min_code_size)
# print(my_compressed_data)

lst2 = lzw_gif3.decompress(my_compressed_data)
assert my_compressed_data == b'\x02\x16\x8c-\x99\x87*\x1c\xdc3\xa0\x02u\xec\x95\xfa\xa8\xde`\x8c\x04\x91L\x01\x00'
assert lst2 == input_indices

import random

random.seed(12629)

for _ in range(100):
    print(_)
    input_indices = [random.randint(0, 3)for _ in range(random.randint(3,6))]
    print(input_indices)
    my_compressed_data = lzw_gif_cpp.compress(input_indices, 2)
    my_compressed_data2 = lzw_gif3.compress(input_indices, 2)
    print(my_compressed_data)
    print(my_compressed_data2)
    assert my_compressed_data == my_compressed_data2
    lst2 = lzw_gif3.decompress(my_compressed_data)
    assert lst2 == input_indices



