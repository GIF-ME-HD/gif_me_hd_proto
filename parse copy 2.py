#!/usr/bin/env python
from PIL import GifImagePlugin
from PIL import Image
from io import BytesIO
import imageio.v3 as iio
import numpy as np
import os
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
	def __init__(self, bytez):
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

	def to_hex_str(self):
		return f'#{self.r}{self.g}{self.b}'

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



# TODO: create our own hash table using python list with our own hash function if there is intensive memory usage issues




# TODO: iniitialize the code table as a hash table which is dependent on the code size given
# NOTE: assume that we already know what code_size to use
def init_gif_lzw_code_table(color_table, code_size=12):
	# The GIF format allows sizes as small as 2 bits and as large as 12 bits. 
	# This minimum code size value is typically the number of bits/pixel of the image.

	# NOTE: the color table is a unique list of RGBTriplets
	N = len(color_table)  # N , the color table size
	
	# NOTE: raise exception if 2 ^ code_size >= color_table_size + 2 (means that the code size is not enough to support the number of possible color indices in the color table   )
	assert(pow(2, code_size) >= N + 2) # +2 because of clear code and EOI code

	# initiailize code table as a hash table, add a code for each color in the color table (covering all the roots)
	# NOTE: using hash table speeds up the searching for a code string for each iteration
	code_table = {}
	for i in range(N):
		rgb_triplet = color_table[i]
		code_table[str(rgb_triplet)] = i	# adds each ASCII character with associated code to the hash table, e.g. table['A'] = 97
	
	# add clear code and EOI code
	i += 1
	code_table["<CC>"] = i
	i += 1
	code_table["<EOI>"] = i

	return code_table





# lzw compression
def lzw_compression(rgb_triplet_image_data, color_table, code_size=2, string_form=True):
	"""
	implemented with the pseudocode given by: http://web.archive.org/web/20050217131148/http://www.danbbs.dk/~dino/whirlgif/lzw.html

	Args:
		data (_type_): _description_
		string_form (bool, optional): _description_. Defaults to True.
	"""
	result = []		
	N = len(color_table)
	code_table = init_gif_lzw_code_table(color_table, code_size)

        
    # the next position to add to the code table
	code = N + 3
    # output <CC> as the very first code
	result.append(code_table["<CC>"])

	w = ''			# prefix is empty
	# loop through every character K in charstream
	for rgb_triplet in rgb_triplet_image_data:
		
		# TODO: make sure that wc fits into the code size used for the table, else outputs <CC> clear code and then  reinitialize code table when we exceed 12 bits (code #4095)
		if code == 4095: # the max range we can go is between #0 and #4095
			# TODO: reinitialize code table
			code_table = init_gif_lzw_code_table(color_table, code_size)

		wc = w + rgb_triplet.to_hex_str()  # current string = prefix + char K  ; the char K in this case is the rgb hex string
		# NOTE: make wc is concatenated RGB triplets in hex string format
		if wc in code_table:
			w = wc	# prefix = current string
		else:
			result.append(code_table[w])  # output code into codestream
			code_table[wc] = code		  # add current string to code table
			code += 1
			w = rgb_triplet.to_hex_str()  # prefix = character K

	# add <EOI> code to the end of the codestream
	result.append(code_table["<EOI>"])

	if string_form:
        # convert the result into a encoded string 
		string = ""
		for item in result:
			string += item
		return string
	else:
		return result
                
                
                

# TODO: converts encoded image data into 
# def lzw_decompression(encoded_data, color_table, code_size):
#     result = []
    
#     # TODO: build the code table
#     code_table = init_gif_lzw_code_table(color_table, code_size)
    
    
#     # TODO: loop through the encoded data (#?)
    
        
    
#     return result





def gif_lzw_decoding(filename):
    # reader = iio.get_reader('DancingPeaks.gif')
    reader = iio.imread(filename, extension=".gif")
    # reader2 = iio.mimread('DancingPeaks.gif', extension=".gif")
    # meta = iio.immeta(filename, extension=".gif")
    
    # with iio.imread('DancingPeaks.gif') as reader:
        # Loop over each frame in the GIF file
    lst = []
    for i, frame in enumerate(reader):
        # Get the image data for the current frame
        image_data = frame.tobytes()
        # frame.properties
        props = iio.improps(filename, index=i)
        meta = iio.immeta(filename, index=i)
        
        # length = len(bytearray(image_data))
        lst.append(image_data)
        try:
            open(f'framedata/{filename}/frame{str(i)}.txt', 'wb')
        except FileNotFoundError:
            os.makedirs(f'framedata/{filename}')
        with open(f'framedata/{filename}/frame{str(i)}.txt', 'wb') as f:
            f.write(image_data)
            
    # similarity = test_similar(lst)

    return lst
                

if __name__ == '__main__':
	import sys
	if len(sys.argv) < 2:
		filename = "sample_1.gif"
	else:
		filename = sys.argv[1]
	reader = GifReader(filename)
	reader.parse()
