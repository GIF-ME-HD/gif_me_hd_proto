from .datareader import DataReader
from .data import GifData, GifFrame, ImageDescriptor, ImageData
from .extensions import Extension
from .utils import is_bit_set, reshape_2d, get_sub_block_size

DEFAULT_HEADER = b"GIF89a"
GIF_TRAILER = 0x3B


class GifReader:
    def __init__(self, filename):
        self.data_reader: DataReader = DataReader(
            filename, len(DEFAULT_HEADER))
        self.__validate_header()

    def __validate_header(self):
        # TODO : have better ways of reading the header out instead.
        if not self.data_reader.bytez.startswith(DEFAULT_HEADER):
            raise Exception("Unsupported Version: " +
                            self.data_reader.bytez[:len(DEFAULT_HEADER)].decode())

    @staticmethod
    def get_ct_size(n):
        return 2 ** (n+1)

    def parse(self) -> GifData:
        """
        Parses the GIF file based loaded.
        """

        """
        <-- HEADER -->
        Signature (3) | Version (3) |

        <-- LOGICAL SCREEN DESCRIPTOR -->
        Logical Screen Width (2u) | Logical Screen Height (2u) |
        Packed Field* (1) | BG Color Index (1) | Pixel Aspect Ratio (1) |

        * Packed Field : {
            GCT Flag (1bit)
            Color Res (3bit)
            Sort Flag (1bit)
            Size of GCT (3bit)
        }
        """
        gif_data = GifData()
        gif_data.width = self.data_reader.read_short()
        gif_data.height = self.data_reader.read_short()

        packed_field = self.data_reader.read_byte()
        gif_data.gct_size = packed_field & 0b000_0111
        gif_data.sort_flag = is_bit_set(packed_field, 3)
        gif_data.color_resolution = packed_field & 0b0111_0000
        gif_data.gct_flag = is_bit_set(packed_field, 7)

        gif_data.bg_color_index = self.data_reader.read_byte()
        gif_data.pixel_aspect_ratio = self.data_reader.read_byte()

        if gif_data.gct_flag:
            gif_data.gct = self.data_reader.read_triplet_list(
                GifReader.get_ct_size(gif_data.gct_size))

        # NOTE: start parsing the frames
        while not self.data_reader.is_done():
            # if end of bytez
            if self.data_reader.peek_byte() == GIF_TRAILER or self.data_reader.offset == len(self.bytez)-1:
                print("DONE")
                self.data_reader.advance(1)

            # TODO: handles all extension, by saving the bytez associated with the extensions first
            elif Extension.is_extension(self.bytez, self.data_reader.offset):
                print("EXTENSION")
                my_ext = Extension.create_extension(
                    self.bytez, self.data_reader.offset)
                self.data_reader.advance(my_ext.size)
                gif_data.frames[frame_ctr].extensions.append(my_ext)
                print(my_ext)

            # Frame Data
            elif ImageDescriptor.is_image_descriptor(self.bytez, self.data_reader.offset):
                """
                <-- IMAGE DESCRIPTOR -->
                ImageSeparator(1) | Left Pos (2u) | Top Pos (2u) | Width (2u) |
                Height (2u) | Packed Fields* (1)

                * Packed Fields : {
                    LCT flag (1bit)
                    Interlace flag (1bit)
                    Sort flag (1bit)
                    Reserved (2bits)
                    Size of LCT (3bits)
                }
                """
                frame = GifFrame()
                gif_data.frames.append(frame)

                frame.img_descriptor = ImageDescriptor()
                self.data_reader.advance(1)
                frame.img_descriptor.left = self.data_reader.read_short()
                frame.img_descriptor.top = self.data_reader.read_short()
                frame.img_descriptor.width = self.data_reader.read_short()
                frame.img_descriptor.height = self.data_reader.read_short()

                packed_field = self.data_reader.read_byte()

                frame.img_descriptor.lct_size = packed_field & 0b0000_0111
                frame.img_descriptor.sort_flag = is_bit_set(packed_field, 5)
                frame.img_descriptor.interlace_flag = is_bit_set(packed_field, 6)
                frame.img_descriptor.lct_flag = is_bit_set(packed_field, 7)

                if frame.img_descriptor.lct_flag:
                    frame.img_descriptor.lct = self.data_reader.read_triplet_list(
                        GifReader.get_ct_size(frame.img_descriptor.lct_size))

                size = get_sub_block_size(self.bytez, self.data_reader.offset)
                # TODO : Parsing of Image Data with LZW Decompression
                self.data_reader.advance(size)

                print(f"ImageData size: {size}")
            
            else:
                raise Exception(f"Unrecognised Block at {self.data_reader.offset}")
        return gif_data


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
            img[x, y] = (b, g, r)
    cv2.imshow(name, img)
    cv2.waitKey(0)
