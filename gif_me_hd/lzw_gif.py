#!/usr/bin/env python

CLEAR_CODE = "CC"
EOI_CODE = "EOI"

class ClearCodeInv:
    def __init__(self):
        pass
class EoiCodeInv:
    def __init__(self):
        pass
def create_code_table(lzw_min_code_size):
    ret = {}
    for i in range(2 ** lzw_min_code_size):
        my_key = ",".join([str(_) for _ in [i]])
        ret[my_key] = i
    ret[CLEAR_CODE] = i+1
    ret[EOI_CODE] = i+2
    return ret

def create_inverse_code_table(lzw_min_code_size):
    ret = {}
    for i in range(2 ** lzw_min_code_size):
        ret[i] = [i]
    ret[i+1] = ClearCodeInv()
    ret[i+2] = EoiCodeInv()
    return ret

def decompress(bytestream):
    index_stream = []
    code_stream = b""
    lzw_min_code_size = bytestream[0]
    code_table = create_inverse_code_table(lzw_min_code_size)
    next_smallest_code = (2 ** lzw_min_code_size)+2
    cur_idx = 1
    subblock_size = bytestream[cur_idx]
    while subblock_size != 0:
        code_stream += bytestream[cur_idx+1:cur_idx+1+subblock_size]
        cur_idx = cur_idx+1+subblock_size
        subblock_size = bytestream[cur_idx]

    get_rightmost_n_bits = lambda x, n: x[0] & (1 << n)-1
    cur_code_size = lzw_min_code_size+1

    # tuple form
    code_stream = (int.from_bytes(code_stream, byteorder='little'), len(code_stream) * 8)

    code = get_rightmost_n_bits(code_stream, cur_code_size)
    code_stream = (code_stream[0] >> cur_code_size, code_stream[1] - cur_code_size)
    assert code == 2 ** lzw_min_code_size

    code = get_rightmost_n_bits(code_stream, cur_code_size)
    code_stream = (code_stream[0] >> cur_code_size, code_stream[1] - cur_code_size)

    index_stream += code_table[code]

    prev_code = code
    codes = [(code, cur_code_size)]
    while True:
        code = get_rightmost_n_bits(code_stream, cur_code_size) # get the current code from byte stream
        code_stream = (code_stream[0] >> cur_code_size, code_stream[1] - cur_code_size) # exhaust the current code from byte stream
        codes.append((code, cur_code_size))
        if code in code_table:
            # encountered clear code 
            if type(code_table[code]) is ClearCodeInv:
                code_table = create_inverse_code_table(lzw_min_code_size)
                next_smallest_code = (2 ** lzw_min_code_size)+2
                cur_code_size = lzw_min_code_size+1

                code = get_rightmost_n_bits(code_stream, cur_code_size)
                code_stream = (code_stream[0] >> cur_code_size, code_stream[1] - cur_code_size)
                codes.append((code, cur_code_size))

                index_stream += code_table[code]
                prev_code = code

                continue
            elif type(code_table[code]) is EoiCodeInv:
                break
            # other codes (not CC or EOI)
            else:
                index_stream += code_table[code]    # output {code}
                k = code_table[code][0]             # k = 1st index in {code}
        else:
            k = code_table[prev_code][0]
            index_stream += code_table[prev_code] + [k] # output {prevcode} + K

        code_table[next_smallest_code] = code_table[prev_code] + [k]    # add {prevcode} + K to code table
        if next_smallest_code == (2 ** cur_code_size)-1 and cur_code_size < 12:
            cur_code_size += 1
        next_smallest_code += 1
        prev_code = code    # update prev code

    return index_stream


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
                code_table[lst_to_str(index_buffer + k)] = next_smallest_code
                code_stream.append((code_table[lst_to_str(index_buffer)], cur_code_size))
                if next_smallest_code == 4096:
                    # Reset
                    code_table = create_code_table(lzw_min_code_size)
                    code_stream.append((code_table[CLEAR_CODE], cur_code_size))
                    cur_code_size = first_code_size
                    index_buffer = k
                    next_smallest_code = (2 ** lzw_min_code_size)+2
                    continue

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

    # making it into one giant block in the form of an integer
    # each sub block is 255 long , we detect if this current sub block is lesser than 255 long
    while len(bytestream) > 0xFE:
        ret += (0xFE).to_bytes(1, byteorder="little")
        ret += bytestream[:0xFE]
        bytestream = bytestream[0xFE:]
    # appending the last sub block that is not 255 long
    if len(bytestream) != 0:
        ret += (len(bytestream)).to_bytes(1, byteorder="little")
        ret += bytestream[:len(bytestream)]
    ret += b"\x00"
    bytestream = bytestream[len(bytestream):]
    
    return ret



if __name__ == '__main__':
    input_indices = [1,1,1,1,1,2,2,2,2,2,1,1,1,1,1,2,2,2,2,2,1,1,1,1,1,2,2,2,2,2,1,1,1,0,0,0,0,2,2,2,1,1,1,0,0,0,0,2,2,2,2,2,2,0,0,0,0,1,1,1,2,2,2,0,0,0,0,1,1,1,2,2,2,2,2,1,1,1,1,1,2,2,2,2,2,1,1,1,1,1,2,2,2,2,2,1,1,1,1,1]
    compressed_data= b'\x02\x16\x8c-\x99\x87*\x1c\xdc3\xa0\x02u\xec\x95\xfa\xa8\xde`\x8c\x04\x91L\x01\x00'
    decompressed_data = decompress(compressed_data)
    print(decompressed_data)
    assert decompressed_data == input_indices
    
    # Future use ceil(log(len(color_table), 2))
    # lzw_min_code_size = compressed_data[0]
    # decompressed_data = input_indices
    # compressed_data = compress(decompressed_data, lzw_min_code_size)
    # print(compressed_data)


