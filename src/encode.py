from data import GifData
from lzw_gif import compress
import math

DEFAULT_HEADER = b"GIF89a"
GIF_TRAILER = 0x3B

class GIF_encoder:
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

    def encode(self, gif_data:GifData):
        self.bytez = DEFAULT_HEADER

        # logical screen descriptor
        self.bytez += gif_data.width.to_bytes(2, byteorder='little')
        self.bytez += gif_data.height.to_bytes(2, byteorder='little')
        packed_field = 0b0000_0000
        packed_field = packed_field | gif_data.gct_size
        packed_field = packed_field | (int(gif_data.sort_flag) << 3)
        packed_field = packed_field | gif_data.color_resolution
        packed_field = packed_field | (int(gif_data.gct_flag) << 7)
        self.bytez += packed_field.to_bytes(1, byteorder='big')

        self.bytez += gif_data.bg_color_index.to_bytes(1, byteorder='big')
        self.bytez += gif_data.pixel_aspect_ratio.to_bytes(1, byteorder='big')

        if gif_data.gct_flag:
            for i in range(2 ** (gif_data.gct_size + 1)):  # the number of RGB triplets is 2^(N+1)
                rgb = gif_data.gct[i]
                self.bytez += rgb.to_byte_string()

        # Extensions
        for ext in gif_data.extensions:
            self.bytez += ext.to_bytes()

        for gifframe in gif_data.frames:
            self.bytez += gifframe.img_descriptor.to_bytez()
            self.bytez += compress(gifframe.frame_img_data, math.ceil(math.log( 2 ** (gif_data.gct_size+1),2)))

        self.bytez += GIF_TRAILER