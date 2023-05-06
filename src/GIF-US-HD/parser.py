from .datareader import DataReader
from .data import GifData, GifFrame, ImageDescriptor, ImageData
from .extensions import Extension
from .utils import is_bit_set, reshape_2d, get_sub_block_size

DEFAULT_HEADER = b"GIF89a"


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
    def get_real_gct_size(n):
        return 2 ** (n+1)


    def parse(self) -> GifData:
        """
        Parses the GIF file based loaded.
        """

        """
        <-- HEADER -->
        Signature (3) | Version (3) |
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
            num_bytes = GifReader.get_real_gct_size(gif_data.gct_size)
            gif_data.gct = self.data_reader.read_triplet_list(num_bytes)

        GIF_TRAILER = 0x3B
        frame_ctr = 0
        image_descriptors = []
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
                # print(f"After extension: {self.bytez[self.dv.offset:]}")

            elif ImageDescriptor.is_image_descriptor(self.bytez, self.data_reader.offset):
                img_descriptor = ImageDescriptor()
                print("IMAGE DESCRIPTOR")
                self.data_reader.advance(1)
                img_descriptor.left = self.data_reader.read_short()
                img_descriptor.top = self.data_reader.read_short()
                img_descriptor.width = self.data_reader.read_short()
                img_descriptor.height = self.data_reader.read_short()

                packed = self.data_reader.read_byte()

                img_descriptor.lct_size = packed & 0b0000_0111
                img_descriptor.sort_flag = is_bit_set(packed, 5)
                img_descriptor.interlace_flag = is_bit_set(packed, 6)
                img_descriptor.lct_flag = is_bit_set(packed, 7)

                if img_descriptor.lct_flag:
                    num_bytes = GifReader.get_real_gct_size(
                        gif_data.img_descriptor.lct_size)
                    lct = self.data_reader.read_triplet_list(num_bytes)
                    img_descriptor.lct = lct

                    from math import sqrt
                    print("Palette:")
                    reshaped_palette = reshape_2d(
                        img_descriptor.lct, int(sqrt(num_bytes)))
                    print(reshaped_palette)
                    display_color_table(
                        reshaped_palette, "LCT " + str(frame_ctr))

                gif_data.img_descriptor = img_descriptor
                # NOTE: add to list of image descriptors
                image_descriptors.append(img_descriptor)

            # It is ImageData
            else:
                frame_ctr += 1
                gif_data.frames.append(GifFrame())
                # Ignore first byte
                print("IMAGE DATA")
                # import binascii
                # print(binascii.hexlify(self.bytez[self.dv.offset:]))

                # TODO: do something with the size, the parsing for the lzw-encoded image data starts here
                minimum_code_size = self.data_reader.read_byte()
                size = get_sub_block_size(self.bytez, self.data_reader.offset)
                # print(binascii.hexlify(self.bytez[self.dv.offset-1:self.dv.offset+size]))

                self.data_reader.advance(size)

                print(f"ImageData size: {size}")

        # TODO: alternatively parse the GIF image data in parallel to the other stuff
        # NOTE: we still assume that image frames sizes  = canvas size
        imagedata_bytez_lst = ImageData.gif_lzw_decoding(
            f"./dataset/DancingPeaks.gif", write_raw_bytes=True)
        frames_rgbs = ImageData.bytez_2_frames_rgb(
            imagedata_bytez_lst, gif_data.width, gif_data.height)

        imagedatas = []
        for i in range(frame_ctr):
            imagedata = ImageData(imagedata_bytez_lst[i])
            imagedata.rgb_lst = frames_rgbs[i]
            imagedatas.append(imagedata)

        # TODO: add ImageData and ImgDescriptor to GifFrames
        for i in range(frame_ctr):
            gif_data.frames[i].img_descriptor = image_descriptors[i]
            gif_data.frames[i].frame_img_data = imagedatas[i]

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
