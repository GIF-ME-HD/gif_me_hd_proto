from .datareader import DataReader
from .data import GifData, GifFrame, ImageDescriptor, ImageData
from .extensions import Extension
from .utils import is_bit_set, reshape_2d, get_sub_block_size

DEFAULT_HEADER = b"GIF89a"

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
        frame_ctr = 0
        image_descriptors = []
        #NOTE: start parsing the frames
        while not self.dv.is_done():
            # if end of bytez
            if self.dv.peek_byte() == GIF_TRAILER or self.dv.offset == len(self.bytez)-1:
                print("DONE")
                self.dv.advance(1)
                
            # TODO: handles all extension, by saving the bytez associated with the extensions first
            elif Extension.is_extension(self.bytez, self.dv.offset):
                print("EXTENSION")
                my_ext = Extension.create_extension(self.bytez, self.dv.offset)
                self.dv.advance(my_ext.size)
                gif_data.frames[frame_ctr].extensions.append(my_ext)
                print(my_ext)
                # print(f"After extension: {self.bytez[self.dv.offset:]}")

            elif ImageDescriptor.is_image_descriptor(self.bytez, self.dv.offset):
                img_descriptor = ImageDescriptor()
                print("IMAGE DESCRIPTOR")
                self.dv.advance(1)
                img_descriptor.left = self.dv.read_short()
                img_descriptor.top = self.dv.read_short()
                img_descriptor.width = self.dv.read_short()
                img_descriptor.height = self.dv.read_short()

                packed = self.dv.read_byte()

                img_descriptor.lct_size = packed & 0b0000_0111
                img_descriptor.sort_flag = is_bit_set(packed, 5)
                img_descriptor.interlace_flag = is_bit_set(packed, 6)
                img_descriptor.lct_flag = is_bit_set(packed, 7)

                if img_descriptor.lct_flag:
                    num_bytes = GifReader.get_real_gct_size(gif_data.img_descriptor.lct_size)
                    lct = self.dv.read_triplet_list(num_bytes)
                    img_descriptor.lct = lct

                    from math import sqrt
                    print("Palette:")
                    reshaped_palette = reshape_2d(img_descriptor.lct, int(sqrt(num_bytes)))
                    print(reshaped_palette)
                    display_color_table(reshaped_palette, "LCT " + str(frame_ctr))

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

                #TODO: do something with the size, the parsing for the lzw-encoded image data starts here
                minimum_code_size = self.dv.read_byte()
                size = get_sub_block_size(self.bytez, self.dv.offset)
                # print(binascii.hexlify(self.bytez[self.dv.offset-1:self.dv.offset+size]))
    
                self.dv.advance(size)
    
                print(f"ImageData size: {size}")


        # TODO: alternatively parse the GIF image data in parallel to the other stuff
        # NOTE: we still assume that image frames sizes  = canvas size
        imagedata_bytez_lst = ImageData.gif_lzw_decoding(f"./dataset/DancingPeaks.gif", write_raw_bytes=True)
        frames_rgbs = ImageData.bytez_2_frames_rgb(imagedata_bytez_lst, gif_data.width, gif_data.height)
        
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
            img[x,y] = (b,g,r)
    cv2.imshow(name, img)
    cv2.waitKey(0)