from __future__ import annotations

from extensions import GraphicsControlExt

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
        self.gct = None

        self.sort_flag = False
        self.color_resolution = None
        self.bg_color_index = 0
        self.pixel_aspect_ratio = 0

        self.extensions = []
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
        
        self.lct = None
    
    @staticmethod
    def is_image_descriptor(bytez, offset):
        if offset >= len(bytez):
            raise Exception("Invalid offset access for image descriptor!!")
        return bytez[offset] == ImageDescriptor.IMAGE_SEPARATOR
    
class RGB:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def __str__(self):
        return f"RGB({self.r}, {self.g}, {self.b})"

    def __repr__(self):
        return str(self)

    @staticmethod
    def to_hex_str(rgb:RGB):
        return f'#{rgb.r}{rgb.g}{rgb.b}'
