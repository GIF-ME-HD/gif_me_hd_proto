#!/usr/bin/env python

CLEAR_CODE = "CC"
EOI_CODE = "EOI"

def create_code_table(lzw_min_code_size):
    ret = {}
    for i in range(2 ** lzw_min_code_size):
        my_key = ",".join([str(_) for _ in [i]])
        ret[my_key] = i
    ret[CLEAR_CODE] = i+1
    ret[EOI_CODE] = i+2
    return ret

def decompress(code_stream):
    lzw_min_code_size = code_stream[0]
    code_table = create_code_table(lzw_min_code_size)

def compress(index_stream, lzw_min_code_size):
    code_stream = b""
    code_stream += lzw_min_code_size.to_bytes(byteorder="big", length=1)
    code_table = create_code_table(lzw_min_code_size)

    lst_to_str = lambda lst: ",".join([str(_) for _ in lst])
    str_to_lst = lambda s: [int(_) for _ in s.split(",")]

    def gen_code_stream(index_stream, lzw_min_code_size, code_table):
        code_stream = []
        first_code_size = lzw_min_code_size+1
        # Send Clear Code
        code_stream.append(2 ** lzw_min_code_size)

        first_val = index_stream[0]
        index_buffer = [first_val]

        next_smallest_code = (2 ** lzw_min_code_size)+2

        for next_ptr in range(1, len(index_stream)):
            k = [index_stream[next_ptr]]

            if lst_to_str(index_buffer+k) in code_table:
                index_buffer = index_buffer + k
            else:
                code_table[lst_to_str(index_buffer + k)] = next_smallest_code
                next_smallest_code += 1
                code_stream.append(code_table[lst_to_str(index_buffer)])
                index_buffer = k
        code_stream += index_buffer
        # Send EOI
        code_stream.append((2 ** lzw_min_code_size) + 1)
        return code_stream
    print(gen_code_stream(index_stream, lzw_min_code_size, code_table))






compressed_data= [0x02, 0x16, 0x8C, 0x2D, 0x99, 0x87, 0x2A, 0x1C, 0xDC, 0x33, 0xA0, 0x02, 0x75, 0xEC, 0x95, 0xFA, 0xA8, 0xDE, 0x60, 0x8C, 0x04, 0x91, 0x4C, 0x01, 0x00]
decompressed_data = decompress(compressed_data)

# Future use ceil(log(len(color_table), 2))
lzw_min_code_size = compressed_data[0]
decompressed_data = [1,1,1,1,1,2,2,2,2,2,1,1,1,1,1,2,2,2,2,2,1,1,1,1,1,2,2,2,2,2,1,1,1,0,0,0,0,2,2,2,1,1,1,0,0,0,0,2,2,2,2,2,2,0,0,0,0,1,1,1,2,2,2,0,0,0,0,1,1,1,2,2,2,2,2,1,1,1,1,1,2,2,2,2,2,1,1,1,1,1,2,2,2,2,2,1,1,1,1,1]
compressed_data = compress(decompressed_data, lzw_min_code_size)


