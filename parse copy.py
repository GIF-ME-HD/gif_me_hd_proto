#!/usr/bin/env python

DEFAULT_HEADER = b"GIF89a"

import struct

class DataReader:
	def __init__(self, bytez, offset=0):
		self.bytez = bytez
		self.length = len(bytez)
		self.offset = offset
	
	def is_done(self):
		return self.offset >= self.length

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
		return RGBTriplet(r, g, b)

	def read_triplet_list(self, num):
		ret = []
		for _ in range(num):
			ret.append(self.read_triplet())
		return ret

	def read_byte_list(self, num):
		ret = []
		for _ in range(num):
			ret.append(self.read_byte())
		return ret
	
	def read_short(self):
		self.check(2)
		ret = struct.unpack_from("<h", self.bytez, offset=self.offset)[0]
		self.advance(2)
		return ret

	def check(self, offset):
		if self.offset + offset <= self.length:
			return True
		else:
			raise Exception("Cannot access value at offset " +
		   str(self.offset+offset))

EXTENSION_FACTORY_METHOD = {
		0xF9: lambda bytez: GraphicsControlExt(bytez),
		0xFE: lambda bytez: CommentExt(bytez),
		0xFF: lambda bytez: Extension(bytez),
		0x01: lambda bytez: Extension(bytez),
}

class Extension:
	def __init__(self, bytez):
		EXTENSION_INTRODUCER = 0x21
		SIZE_INDEX = 2
		self.bytez = bytez
		if self.bytez[0] != EXTENSION_INTRODUCER:
			raise Exception("Not a valid GIF Extension!")
		self.size = len(bytez)

	def validate_identifier(self, identifier, name):
		IDENTIFIER_INDEX = 1
		if self.bytez[IDENTIFIER_INDEX] != identifier:
			raise Exception(f"Not a {name}!")
	
	@staticmethod
	def is_extension(bytez, offset):
		if offset >= len(bytez):
			raise Exception("Invalid offset!")
		return bytez[offset] == 0x21
	
	@staticmethod
	def create_extension(bytez, offset):
		if offset+2 >= len(bytez):
			raise Exception("Invalid Extension index!")
		introducer = bytez[offset]
		ext_type = bytez[offset+1]
		
		size = get_sub_block_size(bytez, offset+2)
		print(f"Extension: {bytez[offset:offset+size+2]}")
		print(f"Ext Size: {size}")
		
		if introducer != 0x21:
			raise Exception("Not a valid GIF Extension!")

		new_bytez = bytez[offset:offset+size+2]
		print(f"3+15+1 = {len(new_bytez)}")
		return EXTENSION_FACTORY_METHOD[ext_type](new_bytez)

class GraphicsControlExt(Extension):
	def __init__(self, bytez):
		IDENTIFIER = 0xF9
		super().__init__(bytez)
		self.size = 8
		if len(bytez) != 8:
			raise Exception("Invalid Graphics Control size!")
		super().validate_identifier(IDENTIFIER, "Graphics Control Extension")

		packed = self.bytez[3]
		self.transparent_color_flag = is_bit_set(packed, 0)
		self.user_input_flag = is_bit_set(packed, 1)
		self.disposal_method = (packed & 0b000_111_00) >> 2
		self.delay_time = (self.bytez[5] << 8) | self.bytez[4] 
		self.transparent_color_index = self.bytez[6]
		print(f"Delay Time: {self.delay_time}")


class CommentExt(Extension):
	def __init__(self, bytez):
		IDENTIFIER = 0xFE
		super().__init__(bytez)
		self.size = bytez[2]+4
		super().validate_identifier(IDENTIFIER, "Comments Extension")
	
	def __repr__(self):
		return f"CommentExt({self.bytez})"

class GifFrame:
	def __init__(self):
		self.extensions = []

class GifData:
	def __init__(self):
		# TO-DO: Add the others
		self.gct = None
		self.width = None
		self.height = None
		self.frames = [GifFrame()]
		self.img_descriptor = ImageDescriptor()

class ImageData:
	def __init__(bytez):
		self.bytez = bytez
	
def get_sub_block_size(bytez, offset):
	start_index = offset
	sample = bytez[start_index]
	size = 0
	print(hex(sample))
	while sample != 0:
		size += sample+1
		sample = bytez[start_index+size]
		print(hex(sample))
		if sample == 0:
			size += 1
	return size

class RGBTriplet:
	def __init__(self, r, g, b):
		self.r = r
		self.g = g
		self.b = b

	def __str__(self):
		return f"RGB({self.r}, {self.g}, {self.b})"

	def __repr__(self):
		return str(self)

def display_color_table(lst, name=''):
	import numpy as np
	import cv2
	img = np.zeros((len(lst), len(lst), 3), np.uint8)
	for x in range(len(lst)):
		for y in range(len(lst)):
			rgb = lst[x][y]
			r = rgb.r
			g = rgb.g
			b = rgb.b
			img[x,y] = (b,g,r)
	cv2.imshow(name, img)
	cv2.waitKey(0)

class ImageDescriptor:
	def __init__(self):
		self.img_left = None
		self.img_top = None
		self.width = None
		self.height = None

		self.lct_flag = None
		self.interlace_flag = None
		self.sort_flag = None

		self.lct_size = None
	
	@staticmethod
	def is_image_descriptor(bytez, offset):
		IMAGE_SEPARATOR = 0x2C
		if offset >= len(bytez):
			raise Exception("Invalid offset access for image descriptor!!")
		return bytez[offset] == IMAGE_SEPARATOR

class GifReader:
	def __init__(self, filename):
		with open(filename, "rb") as f:
			self.bytez = f.read()
		self.dv = DataReader(self.bytez, len(DEFAULT_HEADER))
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

		gif_data.gct = None
		if gif_data.gct_flag:
			num_bytes = GifReader.get_real_gct_size(gif_data.gct_size)
			gct = self.dv.read_triplet_list(num_bytes)
			gif_data.gct = gct

		from math import sqrt
		print("Palette:")
		print(f"Num Bytes: {num_bytes}")
		reshaped_palette = reshape_2d(gif_data.gct, int(sqrt(num_bytes)))
		print(reshaped_palette)
		display_color_table(reshaped_palette, "GCT")

		GIF_TRAILER = 0x3B
		cur_frame = 0

		while not self.dv.is_done():
			if Extension.is_extension(self.bytez, self.dv.offset):
				print("EXTENSION")
				my_ext = Extension.create_extension(self.bytez, self.dv.offset)
				self.dv.advance(my_ext.size)
				gif_data.frames[cur_frame].extensions.append(my_ext)
				print(my_ext)
				# print(f"After extension: {self.bytez[self.dv.offset:]}")
			elif ImageDescriptor.is_image_descriptor(self.bytez, self.dv.offset):
				print("IMAGE DESCRIPTOR")
				self.dv.advance(1)
				gif_data.img_descriptor.left = self.dv.read_short()
				gif_data.img_descriptor.top = self.dv.read_short()
				gif_data.img_descriptor.width = self.dv.read_short()
				gif_data.img_descriptor.height = self.dv.read_short()

				packed = self.dv.read_byte()

				gif_data.img_descriptor.lct_size = packed & 0b0000_0111
				gif_data.img_descriptor.sort_flag = is_bit_set(packed, 5)
				gif_data.img_descriptor.interlace_flag = is_bit_set(packed, 6)
				gif_data.img_descriptor.lct_flag = is_bit_set(packed, 7)

				if gif_data.img_descriptor.lct_flag:
					num_bytes = GifReader.get_real_gct_size(gif_data.img_descriptor.lct_size)
					lct = self.dv.read_triplet_list(num_bytes)
					gif_data.img_descriptor.lct = lct

					from math import sqrt
					print("Palette:")
					reshaped_palette = reshape_2d(gif_data.img_descriptor.lct, int(sqrt(num_bytes)))
					print(reshaped_palette)
					display_color_table(reshaped_palette,
			 "LCT " + str(cur_frame))


			elif self.dv.peek_byte() == GIF_TRAILER or self.dv.offset == len(self.bytez)-1:
				print("DONE")
				self.dv.advance(1)

			# It is ImageData
			else:
				cur_frame += 1
				gif_data.frames.append(GifFrame())
				# Ignore first byte
				print("IMAGE DATA")
				import binascii
				# print(binascii.hexlify(self.bytez[self.dv.offset:]))
    

				#TODO: do something with the size, the parsing for the lzw-encoded image data starts here
				minimum_code_size = self.dv.read_byte()
				size = get_sub_block_size(self.bytez, self.dv.offset)
				# print(binascii.hexlify(self.bytez[self.dv.offset-1:self.dv.offset+size]))
				print(size)
    
    
				self.dv.advance(size)
    

    
    
				print(f"ImageData size: {size}")

				
	
		return gif_data

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

def is_bit_set(data, bit_num):
	return bool(((1 << bit_num) & data))


# TODO: building the lzw code table for image data compression/decompression
def build_lzw_table(color_table, data, string_form = True):
	"""
	inspired by: http://web.archive.org/web/20050217131148/http://www.danbbs.dk/~dino/whirlgif/lzw.html
 
	Args:
		color_table (_type_): _description_
		data (_type_): _description_
		string_form (bool, optional): _description_. Defaults to True.

	Returns:
		_type_: _description_
  
	"""
    
    # 1: initiailize code table as a hash table, add a code for each color in the color table
    
	table = {}
 
    for i in range(256):
        table[chr(i)] = i
        
    # start K with next char in charstream
    code = 256
    
    
    result = []
    w = ''
    for c in data:
        wc = w + c  # current string
        if wc in table:
            w = wc
        else:
            result.append(table[w])  # output code for the 
            table[wc] = code
            code += 1
            w = c
    if w:
        result.append(table[w])
        
        
    # convert the result into a encoded string 
    
    return result


if __name__ == '__main__':
	import sys
	if len(sys.argv) < 2:
		filename = "sample_1.gif"
	else:
		filename = sys.argv[1]
	reader = GifReader(filename)
	reader.parse()
