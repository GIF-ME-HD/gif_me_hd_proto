def is_bit_set(data, bit_num):
    return bool(((1 << bit_num) & data))

def get_sub_block_size(bytez, offset):
    start_index = offset
    sample = bytez[start_index]
    size = 0
    print(hex(sample))
    while sample != 0:
        size += sample+1
        sample = bytez[start_index+size]
        print(hex(sample))
        if sample == 0:
            size += 1
    return size