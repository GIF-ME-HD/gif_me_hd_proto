from __future__ import annotations
import struct

"""
TODO: make changes to GifFrame such that it has:
1. image descriptor frame
2. LCT for a frame
3. image data for a frame
4. extensions (plaintext / comment / application)
"""
class GifFrame:
    def __init__(self):
        self.extensions = []
        self.img_descriptor = None    #  NOTE: the img descriptor contians the LCT (local color table) as well as the width and height of the frame
        self.frame_img_data = None # NOTE: in the form of a 1D list of RGB triplets

class GifData:
    def __init__(self):
        # TODO: Add the others
        self.width = None
        self.height = None

        self.gct_flag = False
        self.gct_size = 0
        self.gct = None

        self.sort_flag = False
        self.color_resolution = None
        self.bg_color_index = 0
        self.pixel_aspect_ratio = 0

        self.frames:list[GifFrame] = []


# TODO: rework the ImageData class for each frame instead of handling for the whole GifData class
class ImageData:
    def __init__(self, bytez):
        # TODO: now we still assume that each image frame matches the canva size of the GIF
        self.bytez = bytez     
        self.rgb_lst = None
    
    def __repr__(self):
        string = f"ImageData[{self.width}x{self.height})]\n"
        for i in range(len(self.frames_rgb)):
            string += f"frame{i}:[{self.frames_rgb[i]}]\n" 
        return string
    
    # TODO: returns list of raw bytes as 2D list of imagedata
    def bytez_2_frames_rgb(bytez_lst, width, height):
        frames_rgb = []
        # calculate the size of the image in bytes
        image_size = width * height * 3
        # loop through each frames' raw bytes
        for i in range(len(bytez_lst)):
            bytez = bytez_lst[i]
            # unpack the raw bytes into RGB triplets
            frame_rgb_data = []
            for j in range(0, image_size, 3):
                r, g, b = struct.unpack("BBB", bytez[j:j+3])
                frame_rgb_data.append(RGB(r, g, b))
            # append rgb triplets in this frame to 
            frames_rgb.append(frame_rgb_data)
        return frames_rgb

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
        
        self.lct = None
    
    @staticmethod
    def is_image_descriptor(bytez, offset):
        IMAGE_SEPARATOR = 0x2C
        if offset >= len(bytez):
            raise Exception("Invalid offset access for image descriptor!!")
        return bytez[offset] == IMAGE_SEPARATOR
    
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
