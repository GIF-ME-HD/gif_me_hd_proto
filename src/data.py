from __future__ import annotations
import struct

from extensions import GraphicsControlExt, Extension

class GifFrame:
    def __init__(self):
        self.graphic_control:GraphicsControlExt = None
        self.img_descriptor:ImageDescriptor = None
        self.frame_img_data:list[int] = None # NOTE: in the form of a 1D list of Indices to CT

class GifData:
    def __init__(self):
        self.width = None
        self.height = None

        self.gct_flag = False
        self.gct_size = 0
        self.gct:list[RGB] = None

        self.sort_flag = False
        self.color_resolution = None
        self.bg_color_index = 0
        self.pixel_aspect_ratio = 0

        self.extensions:list[Extension] = []
        self.frames:list[GifFrame] = []

class ImageDescriptor:
    IMAGE_SEPARATOR = 0x2C
    def __init__(self):
        self.left = None
        self.top = None
        self.width = None
        self.height = None
        
        self.lct_flag = None
        self.interlace_flag = None
        self.sort_flag = None

        self.lct_size = None
        
        self.lct:list[RGB] = None
    
    @staticmethod
    def is_image_descriptor(bytez, offset):
        if offset >= len(bytez):
            raise Exception("Invalid offset access for image descriptor!!")
        return bytez[offset] == ImageDescriptor.IMAGE_SEPARATOR

    def to_bytez(self):
        ret = b"\x2c"
        ret += struct.pack("<H", self.left)
        ret += struct.pack("<H", self.top)
        ret += struct.pack("<H", self.width)
        ret += struct.pack("<H", self.height)
        packed_field = self.lct_size
        packed_field |= int(self.lct_sort_flag) << 5
        packed_field |= int(self.interlace_flag) << 6
        packed_field |= int(self.lct_flag) << 7
        ret += struct.pack("<B", packed_field)
        # followed by the LCT
        if self.lct_flag:
            for i in range(2 ** (self.lct_size + 1)):  # the number of RGB triplets is 2^(N+1)
                rgb = self.lct[i]
                ret += rgb.to_byte_string()
        return ret
    
class RGB:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def __str__(self):
        return f"RGB({self.r}, {self.g}, {self.b})"

    def __repr__(self):
        return str(self)

    def to_byte_string(self):
        return struct.pack("BBB", self.r, self.g, self.b)

    @staticmethod
    def to_hex_str(rgb:RGB):
        return f'#{rgb.r}{rgb.g}{rgb.b}'
