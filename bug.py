#!/usr/bin/env python
from PIL import Image

DEFAULT_HEADER = b"GIF89a"

import struct

class DataReader:
	def __init__(self, bytez, offset=0):
		self.bytez = bytez
		self.length = len(bytez)
		self.offset = offset

	def advance(self, i):
		self.offset += i
		self.check(0)
	
	def peek_byte(self, offset=0):
		self.check(1)
		ret = ord(struct.unpack_from("<c",
			   self.bytez, offset=self.offset)[0])
		return ret

	def read_byte(self):
		ret =  self.peek_byte()
		self.advance(1)
		return ret

	def read_triplet(self):
		r = self.read_byte()
		g = self.read_byte()
		b = self.read_byte()
		return (r, g, b)

	def read_triplet_list(self, num):
		ret = []
		for _ in range(num):
			ret.append(self.read_triplet())
		return ret
	
	def read_short(self):
		self.check(2)
		ret = struct.unpack_from("<h", self.bytez, offset=self.offset)[0]
		self.advance(2)
		return ret

	def check(self, offset):
		if self.offset + offset < self.length:
			return True
		else:
			raise Exception("Cannot access value at offset " +
		   str(self.offset+offset))

class GifData:
	def __init__(self):
		self.global_color_table = None
		self.width = None
		self.height = None

class GifPalette:
	def __init__(self):
		self.data = []

class GifReader:
	def __init__(self, filename):
		with open(filename, "rb") as f:
			self.bytez = f.read()
		self.dv = DataReader(bytez, len(DEFAULT_HEADER))
		self.__validate_header()
	
	def __validate_header(self):
		if not self.bytez.startswith(DEFAULT_HEADER):
			raise Exception("Unsupported Version: " +
		   self.bytez[:len(DEFAULT_HEADER)].decode())
		return True
	
	@staticmethod
	def get_real_gct_size(n):
		return 2 ** (n+1)
	
	def parse(self):
		gif_data = GifData()
		gif_data.width = self.dv.read_short()	
		gif_data.height= self.dv.read_short()	

		packed_field = self.dv.read_byte()
		gif_data.gct_size = packed_field & 0b000_0111
		gif_data.sort_flag = is_bit_set(packed_field, 3)
		gif_data.color_resolution = packed_field & 0b0111_0000
		gif_data.gct_flag = is_bit_set(packed_field, 7)

		gif_data.bf_color_index = self.dv.read_byte()
		gif_data.pixel_aspect_ratio = self.dv.read_byte()

		palette = GifPalette()

		gif_data.gct = None
		if gif_data.gct_flag:
			num_bytes = GifReader.get_real_gct_size(gif_data.gct_size)
			gct = self.dv.read_triplet_list(num_bytes)
			gif_data.gct = gct
		print(gif_data.gct)
		return gif_data

def reshape_2d(lst, num):
	return [[_ for _ in lst[i*num:i*num+num]] for i in range(num)]

def is_bit_set(data, bit_num):
	return bool(((1 << bit_num) & data))

bytez = b""
with open("sample_1.gif", "rb") as f:
	bytez = f.read()

reader = DataReader(bytez)
print(reader.read_byte())
print(reader.read_byte())

reader = GifReader("sample_1.gif")
reader.parse()
