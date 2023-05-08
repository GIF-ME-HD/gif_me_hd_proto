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
    ret = b""
    ret += lzw_min_code_size.to_bytes(byteorder="big", length=1)
    code_table = create_code_table(lzw_min_code_size)

    lst_to_str = lambda lst: ",".join([str(_[0]) for _ in lst])
    str_to_lst = lambda s: [int(_) for _ in s.split(",")]

    def gen_code_stream(index_stream, lzw_min_code_size, code_table):
        code_stream = []
        first_code_size = lzw_min_code_size+1
        cur_code_size = first_code_size

        # Send Clear Code
        code_stream.append((code_table[CLEAR_CODE], cur_code_size))

        first_val = index_stream[0]
        index_buffer = [(first_val, cur_code_size)]

        next_smallest_code = (2 ** lzw_min_code_size)+2

        for next_ptr in range(1, len(index_stream)):
            k = [(index_stream[next_ptr], cur_code_size)]

            if lst_to_str(index_buffer+k) in code_table:
                index_buffer = index_buffer + k
            else:
                if next_smallest_code == 4096:
                    # Reset
                    code_table = create_code_table(lzw_min_code_size)
                    code_stream.append((code_table[CLEAR_CODE], cur_code_size))
                    index_buffer = k
                    next_smallest_code = (2 ** lzw_min_code_size)+2

                code_table[lst_to_str(index_buffer + k)] = next_smallest_code
                code_stream.append((code_table[lst_to_str(index_buffer)], cur_code_size))
                if next_smallest_code == 2 ** cur_code_size:
                    cur_code_size += 1
                next_smallest_code += 1
                index_buffer = k
                
        code_stream.append((code_table[lst_to_str(index_buffer)], cur_code_size))
        
        # Send EOI
        code_stream.append((code_table[EOI_CODE], cur_code_size))
        return code_stream
    code_stream = gen_code_stream(index_stream, lzw_min_code_size, code_table)

    def append_bits(a, b):
        num_a, num_a_len = a
        num_b, num_b_len = b
        return ((num_a << num_b_len) | num_b, num_a_len + num_b_len)

    bitstream = (0, 0)
    for code in code_stream:
        bitstream = append_bits(code, bitstream)

    # Padding
    pad_num = 8 - (bitstream[1] % 8)
    bitstream = (bitstream[0], bitstream[1] + pad_num)

    bytestream = bitstream[0].to_bytes(byteorder="little", length=bitstream[1] // 8)

    while len(bytestream) > 0xFF:
        ret += (0xFF).to_bytes(1, byteorder="little")
        ret += bytestream[:0xFF]
        bytestream = bytestream[0xFF:]
        
    ret += (len(bytestream)).to_bytes(1, byteorder="little")
    ret += bytestream[:len(bytestream)]
    ret += b"\x00"
    bytestream = bytestream[len(bytestream):]

    return ret



# test case 1
compressed_data= b'\x02\x16\x8c-\x99\x87*\x1c\xdc3\xa0\x02u\xec\x95\xfa\xa8\xde`\x8c\x04\x91L\x01\x00'
decompressed_data = decompress(compressed_data)

# Future use ceil(log(len(color_table), 2))
lzw_min_code_size = compressed_data[0]
decompressed_data = [1,1,1,1,1,2,2,2,2,2,1,1,1,1,1,2,2,2,2,2,1,1,1,1,1,2,2,2,2,2,1,1,1,0,0,0,0,2,2,2,1,1,1,0,0,0,0,2,2,2,2,2,2,0,0,0,0,1,1,1,2,2,2,0,0,0,0,1,1,1,2,2,2,2,2,1,1,1,1,1,2,2,2,2,2,1,1,1,1,1,2,2,2,2,2,1,1,1,1,1]
compressed_data = compress(decompressed_data, lzw_min_code_size)
print(compressed_data)


