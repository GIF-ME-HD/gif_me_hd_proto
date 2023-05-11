#include <cmath>
#include <iostream>
#include <memory>
#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
#include <vector>

#include "bitreader.h"
namespace py = pybind11;

struct CodeTableNode;

typedef std::unique_ptr<CodeTableNode> CTNodePtr;

struct CodeTableNode {
  int value;
  std::vector<CodeTableNode *> children;
  int clear_code;
  int eoi_code;

  CodeTableNode(int val) : value(val), clear_code(-1), eoi_code(-1) {
    this->children.resize(256, nullptr);
  }
  ~CodeTableNode() {
    for (auto child : children) {
      if (child) {
        delete child;
      }
    }
  }
};

CodeTableNode *CreateCodeTable(int lzw_min_code_size) {
  CodeTableNode *root = new CodeTableNode(-100);
  int i = 0;

  for (i = 0; i < static_cast<int>(std::pow(2, lzw_min_code_size)); i++) {
    root->children[i] = new CodeTableNode(i);
  }
  root->clear_code = i;
  root->eoi_code = i + 1;

  return root;
}

std::vector<std::pair<int, int>>
gen_code_stream(const std::vector<int> &index_stream, int lzw_min_code_size,
                CodeTableNode *code_table_root) {
  std::vector<std::pair<int, int>> code_stream;
  int first_code_size = lzw_min_code_size + 1;
  int cur_code_size = first_code_size;

  // Send Clear Code
  code_stream.push_back({code_table_root->clear_code, cur_code_size});

  int first_val = index_stream[0];

  int next_smallest_code = (1 << lzw_min_code_size) + 2;
  CodeTableNode *cur_table_node = code_table_root->children[first_val];
  std::cout << "A"
            << "\n";
  CodeTableNode *abc = code_table_root->children[3];
  std::cout << "abc: " << abc << "\n";

  for (size_t next_ptr = 1; next_ptr < index_stream.size(); next_ptr++) {
    std::cout << next_ptr << "\n";
    std::cout << "GETTING VAL"
              << "\n";

    int k = index_stream[next_ptr];
    std::cout << "RETRIEVED VAL " << k << "\n";

    std::cout << "Out of " << cur_table_node << "\n";

    if (cur_table_node->children[k] != NULL) {
      std::cout << "OO " << cur_table_node->children[k] << "\n";
      cur_table_node = cur_table_node->children[k];
      std::cout << "PP"
                << "\n";
    } else {
      std::cout << "XX"
                << "\n";
      cur_table_node->children[k] = new CodeTableNode(next_smallest_code);
      std::cout << "YY"
                << "\n";
      code_stream.push_back({cur_table_node->value, cur_code_size});

      if (next_smallest_code == 4096) {
        // Reset
        delete code_table_root;
        code_table_root = CreateCodeTable(lzw_min_code_size);
        code_stream.push_back({code_table_root->clear_code, cur_code_size});
        cur_table_node = code_table_root->children[k];
        next_smallest_code = (1 << lzw_min_code_size) + 2;
        cur_code_size = lzw_min_code_size + 1;
        continue;
      }

      if (next_smallest_code == (1 << cur_code_size)) {
        cur_code_size += 1;
      }
      next_smallest_code += 1;
      cur_table_node = code_table_root->children[k];
    }
  }

  code_stream.push_back({cur_table_node->value, cur_code_size});

  // Send EOI
  code_stream.push_back({code_table_root->eoi_code, cur_code_size});

  return code_stream;
}

std::vector<int> compress_lzw_gif(const std::vector<int> &index_stream,
                                  int lzw_min_code_size) {

  auto append_bits = [](std::pair<int, int> &a, std::pair<int, int> &b) {
    int num_a = a.first;
    int num_a_len = a.second;
    int num_b = b.first;
    int num_b_len = b.second;

    return std::make_pair((num_a << num_b_len) | num_b, num_a_len + num_b_len);
  };

  std::vector<int> ret;

  // Write lzw_min_code_size
  ret.push_back(lzw_min_code_size);

  CodeTableNode *code_table_root = CreateCodeTable(lzw_min_code_size);
  std::vector<std::pair<int, int>> code_stream =
      gen_code_stream(index_stream, lzw_min_code_size, code_table_root);

  // Convert code stream to bit stream
  //
  std::pair<int, int> bitstream = std::make_pair(0, 0);
  for (auto &code : code_stream) {
    std::cout << "YY " << code.first << "\n";
    bitstream = append_bits(code, bitstream);
  }

  // Padding
  int pad_num = 8 - (bitstream.second % 8);
  bitstream =
      std::make_pair((bitstream.first << pad_num) | ((1 << pad_num) - 1),
                     bitstream.second + pad_num);

  // Convert bit stream to byte stream
  std::vector<uint8_t> bytestream;
  for (int i = 0; i < bitstream.second / 8; i++) {
    bytestream.push_back((bitstream.first >> (i * 8)) & 0xFF);
  }

  // Write byte stream to output vector, with length prefixes
  while (bytestream.size() > 0xFE) {
    ret.push_back(0xFE);
    ret.insert(ret.end(), bytestream.begin(), bytestream.begin() + 0xFE);
    bytestream.erase(bytestream.begin(), bytestream.begin() + 0xFE);
  }
  if (bytestream.size() > 0) {
    ret.push_back(bytestream.size());
    ret.insert(ret.end(), bytestream.begin(), bytestream.end());
  }
  ret.push_back(0x00);

  return ret;
}

int add(int i, int j) { return i + j; }
#include <iomanip>
#include <sstream>

py::bytes compress(const std::vector<int> &indices, int lzw_min_code_size) {
  std::vector<char> ret;
  for (auto item : indices) {
    std::cout << item << "\n";
  }
  std::vector<int> temp = compress_lzw_gif(indices, lzw_min_code_size);
  std::string result(temp.begin(), temp.end());

  return py::bytes(result);
  // return py::bytes("\xde\xad\xba\xbe");
}

PYBIND11_MODULE(lzw_gif_cpp, m) {
  m.doc() = "pybind11 lzw gif compression";

  m.def("add", &add, "A function that adds two numbers");
  m.def("compress", &compress, "A function that compresses a list of indices");
}
