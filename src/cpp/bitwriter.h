#include <iostream>
#include <vector>
class BitWriter {
public:
  std::vector<unsigned char> stream;
  int bit_offset;

public:
  void add_n_bits(int num, int len) {
    if (bit_offset == 8) {
      bit_offset = 0;
      stream.push_back(0);
    }
    int remainder_current_byte = 8 - bit_offset;
    if (len < remainder_current_byte) {
      stream.back() = stream.back() | (num << bit_offset);
      bit_offset += len;
    } else if (len == remainder_current_byte) {
      stream.back() = stream.back() | (num << bit_offset);
      bit_offset += len;
    } else {
      int mask = (1 << remainder_current_byte) - 1;
      int temp = num & mask;
      stream.back() = stream.back() | (temp << bit_offset);
      num >>= remainder_current_byte;
      len -= remainder_current_byte;
      bit_offset = len % 8;

      while (len > 0) {
        mask = (1 << 8) - 1;
        temp = num & mask;
        num >>= 8;
        stream.push_back(temp);
        len -= 8;
      }
      if (len == 0) {
        stream.push_back(0);
      }
    }
  }
  BitWriter() : bit_offset(0) { stream.push_back(0); }
  ~BitWriter() {}
};
