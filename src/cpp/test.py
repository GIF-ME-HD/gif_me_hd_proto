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

import sys

input_indices = [21, 54, 38, 8, 43, 24, 21, 53, 50, 56, 45, 10, 41, 36, 15, 21, 23, 25, 14, 20, 37, 11, 10, 42, 6, 49, 54, 42, 26, 6, 2, 54, 0, 34, 36, 49, 8, 2, 18, 19, 43, 5, 23, 44, 18, 12, 57, 53, 43, 6, 35, 31, 47, 9, 7, 13, 25, 24, 6, 9, 55, 26, 43, 52, 23, 48, 48, 34, 29, 30, 3, 55, 56, 26, 28, 17, 11, 50, 38, 4, 55, 41, 48, 23, 26, 25, 34, 28, 43, 10, 57, 5, 2, 25, 29, 10, 19, 48, 37, 1, 52, 56, 7, 36, 35, 42, 29, 4, 2, 6, 48, 56, 19, 6, 28, 34, 20, 21, 4, 43, 32, 1, 11, 16, 27, 5, 16, 3, 44, 30, 33, 30, 36, 21]
my_compressed_data2 = lzw_gif3.compress(input_indices, 7)
my_compressed_data = lzw_gif_cpp.compress(input_indices, 7)
print(my_compressed_data)
print(my_compressed_data2)

# sys.exit()

import random

random.seed(12629)

_ = 0
old_len = 2 ** 1000
while True:
    input_indices = [random.randint(0, 58)for _ in range(random.randint(3,300))]
    # print(input_indices)
    my_compressed_data2 = lzw_gif3.compress(input_indices, 7)
    my_compressed_data = lzw_gif_cpp.compress(input_indices, 7)
    # print(my_compressed_data)
    # print(my_compressed_data2)
    if my_compressed_data != my_compressed_data2 and len(input_indices) < old_len:
        print(f"Attempt #{_} with lzw_min_code_size=6 length {len(input_indices)}")
        print(input_indices)
        old_len = len(input_indices)
        continue
    # assert my_compressed_data == my_compressed_data2
    # lst2 = lzw_gif3.decompress(my_compressed_data)
    # assert lst2 == input_indices
    _ += 1



