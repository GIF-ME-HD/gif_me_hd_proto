import timeit
from data import GifData
from lzw_gif import compress as c1
from lzw_gif2 import compress as c2
from lzw_gif3 import compress as c3

from lzw_gif_cpp import compress as compress_cpp
import math

DEFAULT_HEADER = b"GIF89a"
GIF_TRAILER = b"\x3B"

class GifEncoder:
    def __init__(self, filename):
        self.filename = filename
        self.bytes = None

    def add_bytes(self, bytez, places):
        # shift left for self.bytez by places
        self.bytez = self.bytez << places
        # add the bytez to the self.bytez
        self.bytez = self.bytez | bytez

    def to_file(self):
        assert (self.bytez is not None)
        with open(self.filename, "wb") as f:
            f.write(self.bytez)

    def encode(self, gif_data:GifData, compressfunc):
        self.bytez = DEFAULT_HEADER

        # logical screen descriptor
        self.bytez += gif_data.width.to_bytes(2, byteorder='little')
        self.bytez += gif_data.height.to_bytes(2, byteorder='little')
        packed_field = 0b0000_0000
        packed_field = packed_field | gif_data.gct_size
        packed_field = packed_field | (int(gif_data.sort_flag) << 3)
        packed_field = packed_field | gif_data.color_resolution
        packed_field = packed_field | (int(gif_data.gct_flag) << 7)
        self.bytez += packed_field.to_bytes(1, byteorder='little')

        self.bytez += gif_data.bg_color_index.to_bytes(1, byteorder='little')
        self.bytez += gif_data.pixel_aspect_ratio.to_bytes(1, byteorder='little')

        if gif_data.gct_flag:
            for i in range(2 ** (gif_data.gct_size + 1)):  # the number of RGB triplets is 2^(N+1)
                rgb = gif_data.gct[i]
                self.bytez += rgb.to_byte_string()

        # Extensions
        for ext in gif_data.extensions:
            self.bytez += ext.to_bytes()

        for i, gifframe in enumerate(gif_data.frames):
            # print(f"Encoding Frame {i}")
            if not gifframe.graphic_control.hidden:
                self.bytez += gifframe.graphic_control.to_bytes()
            self.bytez += gifframe.img_descriptor.to_bytez()
            self.bytez += compressfunc(gifframe.frame_img_data, math.ceil(math.log( 2 ** (gif_data.gct_size+1),2)))

        self.bytez += GIF_TRAILER
        

if __name__ == "__main__":
    from parse import GifReader
    filename = "../dataset/esqueleto.gif"
    from time import time
    
    gif_reader = GifReader(filename)
    gif_data = gif_reader.parse()

    # time1 = time()
    # encoder = GifEncoder("output1.gif")
    # encoder.encode(gif_data, c1)
    # encoder.to_file()
    # time2 = time()
    # print("Time taken for c1: ", time2-time1)
    #
    # time1 = time()
    # encoder = GifEncoder("output2.gif")
    # encoder.encode(gif_data, c2)
    # encoder.to_file()
    # time2 = time()
    # print("Time taken for c2: ", time2-time1)

    time1 = time()
    encoder = GifEncoder("c3_output3.gif")
    encoder.encode(gif_data, c3)
    encoder.to_file()
    time2 = time()
    print("Time taken for c3: ", time2-time1)

    time1 = time()
    encoder = GifEncoder("cpp_output3.gif")
    encoder.encode(gif_data, compress_cpp)
    encoder.to_file()
    time2 = time()
    print("Time taken for compress_cpp: ", time2-time1)

    print("Done!")
