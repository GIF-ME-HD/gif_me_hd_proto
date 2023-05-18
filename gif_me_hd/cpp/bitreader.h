#include <bitset>
#include <iostream>

class BitReader {
public:
  BitReader(const char *data, size_t length, size_t offset = 0)
      : bytez(data), length(length), byte_offset(offset), bit_offset(0) {}

  uint32_t read_n_bits(size_t num_bits) {
    uint32_t ret = 0;
    size_t read_bits_so_far = 0;
    size_t remainder_bits_current_byte = 8 - bit_offset;
    if (num_bits >= remainder_bits_current_byte) {
      uint8_t mask = (1 << remainder_bits_current_byte) - 1;
      mask <<= bit_offset;
      uint32_t to_app = bytez[byte_offset] & mask;
      to_app >>= bit_offset;
      ret |= to_app << read_bits_so_far;
      bit_offset += remainder_bits_current_byte;
      num_bits -= remainder_bits_current_byte;
      read_bits_so_far += remainder_bits_current_byte;
      if (bit_offset == 8) {
        byte_offset += 1;
        bit_offset = 0;
      }
    }

    while (num_bits > 8) {
      ret |= bytez[byte_offset] << read_bits_so_far;
      byte_offset += 1;
      num_bits -= 8;
      read_bits_so_far += 8;
    }

    remainder_bits_current_byte = 8 - bit_offset;
    if (num_bits > 0 && num_bits <= remainder_bits_current_byte) {
      uint8_t mask = (1 << num_bits) - 1;
      mask <<= bit_offset;
      uint32_t to_app = bytez[byte_offset] & mask;
      to_app >>= bit_offset;
      ret |= to_app << read_bits_so_far;
      bit_offset += num_bits;
      if (bit_offset == 8) {
        byte_offset += 1;
        bit_offset = 0;
      }
    }
    return ret;
  }

private:
  const char *bytez;
  size_t length;
  size_t byte_offset;
  size_t bit_offset;
};

int main() {
  BitReader a("ab", 2);
  std::cout << std::bitset<8>(a.read_n_bits(8)) << std::endl;
  std::cout << std::bitset<8>(a.read_n_bits(8)) << std::endl;
  return 0;
}
