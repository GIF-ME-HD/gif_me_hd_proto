#!/usr/bin/env python
import copy
from gif_me_hd.bitreader import BitReader

CLEAR_CODE = "CC"
EOI_CODE = "EOI"

CLEAR_CODE_IDX = -1
EOI_CODE_IDX = -2


class ClearCodeInv:
    def __init__(self):
        pass


class EoiCodeInv:
    def __init__(self):
        pass


def create_inverse_code_table(lzw_min_code_size):
    ret = {}
    for i in range(2 ** lzw_min_code_size):
        ret[i] = [i]
    ret[i + 1] = ClearCodeInv()
    ret[i + 2] = EoiCodeInv()
    return ret

def decompress(bytestream):
    index_stream = []
    code_stream = b""
    lzw_min_code_size = bytestream[0]
    code_table = create_inverse_code_table(lzw_min_code_size)
    next_smallest_code = (2 ** lzw_min_code_size) + 2
    cur_idx = 1
    subblock_size = bytestream[cur_idx]
    while subblock_size != 0:
        code_stream += bytestream[cur_idx + 1:cur_idx + 1 + subblock_size]
        cur_idx = cur_idx + 1 + subblock_size
        subblock_size = bytestream[cur_idx]

    cur_code_size = lzw_min_code_size + 1

    # tuple form
    code_stream = BitReader(code_stream)

    code = code_stream.read_n_bits(cur_code_size)
    assert code == 2 ** lzw_min_code_size

    code = code_stream.read_n_bits(cur_code_size)
    index_stream += code_table[code]

    prev_code = code
    codes = [code]
    while True:
        code = code_stream.read_n_bits(cur_code_size)
        codes.append(code)
        if code in code_table:
            # encountered clear code
            if type(code_table[code]) is ClearCodeInv:
                code_table = create_inverse_code_table(lzw_min_code_size)
                next_smallest_code = (2 ** lzw_min_code_size) + 2
                cur_code_size = lzw_min_code_size + 1

                code = code_stream.read_n_bits(cur_code_size)

                index_stream += code_table[code]
                prev_code = code

                continue
            elif type(code_table[code]) is EoiCodeInv:
                break
            # other codes (not CC or EOI)
            else:
                index_stream += code_table[code]  # output {code}
                k = code_table[code][0]  # k = 1st index in {code}
        else:
            k = code_table[prev_code][0]
            index_stream += code_table[prev_code] + [k]  # output {prevcode} + K

        code_table[next_smallest_code] = code_table[prev_code] + [k]  # add {prevcode} + K to code table
        if next_smallest_code == (2 ** cur_code_size) - 1 and cur_code_size < 12:
            cur_code_size += 1
        next_smallest_code += 1
        prev_code = code  # update prev code

    return index_stream


def create_code_table_inverse(lzw_min_code_size):
    root = CodeTableNode()
    for i in range(2 ** lzw_min_code_size):
        root.children.append((i, CodeTableNode()))

    clear_code = CodeTableNode()
    clear_code.is_clear_code = True
    root.children.append((i + 1, clear_code))

    eoi_code = CodeTableNode()
    eoi_code.is_eoi_code = True
    root.children.append((i + 2, eoi_code))


class CodeTableNode:
    def __init__(self, val):
        self.value = val
        self.children = [None] * 256
        self.is_clear_code = False
        self.is_eoi_code = False


ct_rets = []
for _ in range(100):
    ct_rets.append(None)
def create_code_table(lzw_min_code_size):
    if ct_rets[lzw_min_code_size] is not None:
        return copy.deepcopy(ct_rets[lzw_min_code_size])

    root = CodeTableNode('root')
    for i in range(2 ** lzw_min_code_size):
        root.children[i] = CodeTableNode(i)

    root.clear_code = i+1
    root.eoi_code = i+2

    ct_rets[lzw_min_code_size] = copy.deepcopy(root)

    return root


def compress(index_stream, lzw_min_code_size):
    ret = b""
    ret += lzw_min_code_size.to_bytes(byteorder="big", length=1)
    code_table_root = create_code_table(lzw_min_code_size)

    def gen_code_stream(index_stream, lzw_min_code_size, code_table_root):
        code_stream = []
        first_code_size = lzw_min_code_size + 1
        cur_code_size = first_code_size

        # Send Clear Code
        code_stream.append((code_table_root.clear_code, cur_code_size))

        first_val = index_stream[0]

        next_smallest_code = (2 ** lzw_min_code_size) + 2
        cur_table_node = code_table_root.children[first_val]

        for next_ptr in range(1, len(index_stream)):
            k = (index_stream[next_ptr], cur_code_size)

            if cur_table_node.children[k[0]] is not None:
                cur_table_node = cur_table_node.children[k[0]]
            else:
                cur_table_node.children[k[0]] = CodeTableNode(next_smallest_code)
                code_stream.append((cur_table_node.value, cur_code_size))

                if next_smallest_code == 4096:
                    # Reset
                    code_table_root = create_code_table(lzw_min_code_size)
                    code_stream.append((code_table_root.clear_code, cur_code_size))
                    cur_table_node = code_table_root.children[k[0]]
                    next_smallest_code = (2 ** lzw_min_code_size) + 2
                    cur_code_size = lzw_min_code_size + 1
                    continue

                if next_smallest_code == 2 ** cur_code_size:
                    cur_code_size += 1
                next_smallest_code += 1
                cur_table_node = code_table_root.children[k[0]]
        code_stream.append((cur_table_node.value, cur_code_size))
        # Send EOI
        code_stream.append((code_table_root.eoi_code, cur_code_size))
        return code_stream

    code_stream = gen_code_stream(index_stream, lzw_min_code_size, code_table_root)

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

    while len(bytestream) > 0xFE:
        ret += (0xFE).to_bytes(1, byteorder="little")
        ret += bytestream[:0xFE]
        bytestream = bytestream[0xFE:]
    if len(bytestream) != 0:
        ret += (len(bytestream)).to_bytes(1, byteorder="little")
        ret += bytestream[:len(bytestream)]
    ret += b"\x00"
    bytestream = bytestream[len(bytestream):]

    return ret


if __name__ == '__main__':
    input_indices = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 1,
                     0, 0, 0, 0, 2, 2, 2, 1, 1, 1, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 0, 0, 0,
                     0, 1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 1, 1,
                     1]
    compressed_data = b'\x02\x16\x8c-\x99\x87*\x1c\xdc3\xa0\x02u\xec\x95\xfa\xa8\xde`\x8c\x04\x91L\x01\x00'
    decompressed_data = decompress(compressed_data)
    print(decompressed_data)
    assert decompressed_data == input_indices

    # # Future use ceil(log(len(color_table), 2))
    lzw_min_code_size = compressed_data[0]
    decompressed_data = input_indices
    my_compressed_data = compress(decompressed_data, lzw_min_code_size)
    assert compressed_data == my_compressed_data


