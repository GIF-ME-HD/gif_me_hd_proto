def is_bit_set(data, bit_num):
    return bool(((1 << bit_num) & data))

def get_sub_block_size(bytez, offset):
    start_index = offset
    sample = bytez[start_index]
    size = 0
    while sample != 0:
        size += sample+1
        sample = bytez[start_index+size]
        if sample == 0:
            size += 1
    return size

def reshape_2d(lst, num):
    ret = [None] * num
    for _ in range(num):
        ret[_] = [None] * num

    i = 0
    for y in range(num):
        for x in range(num):
            to_add = None
            if i < len(lst):
                to_add = lst[i]
                i += 1
            ret[y][x] = to_add
    return ret