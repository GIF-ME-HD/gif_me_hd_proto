


def prepend_bits(to_prepend, result):
    to_prepend_bits, to_prepend_len = to_prepend
    results_bits, results_len = result
    return (to_prepend_bits << results_len) | results_bits, to_prepend_len + results_len


def prepend_code(code, code_size, result):
    
    return prepend_bits((code, code_size), result)


result = prepend_bits((0b1111, 4), (0b01111, 5))

print(bin(result[0]), result[1])

result = 0b11110100, 8
result = prepend_code(4,3,result)
print(bin(result[0]), result[1] )