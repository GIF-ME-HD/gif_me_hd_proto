import struct
from PIL import GifImagePlugin
from PIL import Image
from io import BytesIO
import imageio.v3 as iio
import numpy as np
import os
HEADER = b'\x47\x49\x46\x38\x39\x61' #GIF89a


def parseGIF(bytez):
    # HEADER Block (Byte 0 -> 5)
    # Verify is GIF + Right Version
    # if not bytez.startswith(HEADER):
    #     print('This is not a GIF89a compliant GIF File!')
    #     return None

    bytearr = bytearray(bytez)

    # Logical Screen Descriptor Block (Byte 6 -> 13)
    width,height = struct.unpack('<2h', bytearr[0x6:0xA])
    #  <Packed Fields>  =  Global Color Table Flag       1 Bit
    #                      Color Resolution              3 Bits
    #                      Sort Flag                     1 Bit
    #                      Size of Global Color Table    3 Bits
    packed_fields = bytearr[0xA]
    flag_GCT = packed_fields & 0b10000000
    color_res = packed_fields & 0b01110000 >> 4
    flag_GCTSort = packed_fields & 0b00001000
    size_GCT = packed_fields & 0b00000111

    index_background = bytearr[0xB]
    pixel_aspect_ratio = bytearr[0xC]
    aspect_ratio = (pixel_aspect_ratio + 15) / 64

    # Global Color Table Block (Byte 14->3x(2^size_GCT)+14) If GCT Present
    if flag_GCT:
        GCT = [0]*(2^size_GCT)
        for i in range(2^size_GCT):
            GCT[i] = (bytearr[0x14+3*i], bytearr[0x14+3*i+1], bytearr[0x14+3*i+2])
    
    #TODO Image Descriptor & Frame
    # Image Descriptor & Each Frame
    # For amount of frames, parse image descriptor for frame and frame data
    

    
    
    
# needs to add a code for each color in the color table
def build_lzw_codetable(colortable):
    # build the code table
    pass


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
            
    similarity = test_similar(lst)

    return lst


def txt_to_jpg(txt_path, jpg_path, width, height):
    # create a new image object
    image = Image.new("RGB", (width, height))

    # open the text file and read the RGB data
    with open(txt_path, "r") as f:
        data = f.read().splitlines()

    # loop through the data and set the pixel colors
    for y in range(height):
        for x in range(width):
            # get the RGB values for the current pixel
            r, g, b = map(int, data[y * width + x].split(","))
            # set the pixel color
            image.putpixel((x, y), (r, g, b))

    # save the image as a JPG file
    image.save(jpg_path)



def visualize_frame(directory_path, txt_filename, gif_filename, output_format="open"):    
    with Image.open(gif_filename) as giffile:
        width,height = giffile.width, giffile.height
    
    with open(f"{directory_path}/{txt_filename}", 'rb') as f:
        image_bytes = f.read()
        
    # Use Pillow's Image.open() method to open the image from the stream
    # image = Image.open(stream)
    # image = Image.frombytes(image_bytes)
    # print(len(stream))
    # width,height = 435,343
    arr = np.asarray(bytearray(image_bytes))
    
    arr = arr.reshape((height, width, 3))
    
    im = Image.fromarray(arr, mode="RGB")
    # im.getpixel((0, 0))  # (44, 1, 0)

    # Now you can use the image variable to display or manipulate the image
    if output_format == "open":
        im.show()
    elif output_format == "file":
        txt_to_jpg(f"{directory_path}/{txt_filename}", f"./framedata/jpg_output/{txt_filename[:-3]}.jpg", width, height)
    else:
        print("Invalid output format")
        
    return None
    
    
# get all filenames in directory
def get_filenames(directory):
    filenames = []
    for filename in os.listdir(directory):
        filenames.append(filename)
    return filenames


def test_similar(lst):
    flag = True
    for i in range(len(lst)):
        for j in range(len(lst)):
            if not (lst[i] == lst[j]):
                flag = False
                return flag
    return flag



# def gif_lzw_decoding():
#     # initialize code table
#     img = Image.open('DancingPeaks.gif')
    
#     data = img.getdata()
#     flag = img.is_animated
    
#     # frame1 = img.seek()
    
#     img.show()
    
#     lst = []
#     lst.append(img.tobytes())
#     img.save('frame0.gif')
#     for i in range(1, img.n_frames):
#         # img.show()
#         img.seek(img.tell()+1)
#         lst.append(img.tobytes())
#         img.save('frame'+str(i)+'.gif')
    

#     for i in range(len(lst)):
#         # Convert bytes to image using Pillow
#         with Image.open(BytesIO(lst[i])) as im:
#             # Do something with the image, e.g. display or save it
#             im.show()
            
    
    
#     img.close()
    
    
    
    
    # let CODE be the first code in the code stream
    
    
    # output {CODE} to index stream
    
    
    # set PREVCODE = CODE
    
    
    # <LOOP POINT>
    # let CODE be the next code in the code stream
    # is CODE in the code table?
    # Yes:
    # output {CODE} to index stream
    # let K be the first index in {CODE}
    # add {PREVCODE}+K to the code table
    # set PREVCODE = CODE
    # No:
    # let K be the first index of {PREVCODE}
    # output {PREVCODE}+K to index stream
    # add {PREVCODE}+K to code table
    # set PREVCODE = CODE
    # return to LOOP POINT
        
        
        
        
    
    
    
    
def parseImageBlocks(size, bytes):
    ret_arr = []
    # this happens after parsiung the global color table and then the graphic control extension (which is optional)
    
        
    
    # first byte is the lzw minimum code size
    lzw_min_codesize = bytes[0]
    
    # rest of the bytes are data sub-blocks
    sub_blocks = bytes[1:]
    
    
    # first byte of each data sub-block tells how bytes of actual data to follow
    subblock_size = sub_blocks[0];
    bytes_counter = 0
    while subblock_size != 0: # while we havbent met block terminator
        for i in range(subblock_size):
            # refer to the color code table
            # append something to the ret_arr
            pass
        
        bytes_counter += subblock_size
        subblock_size = sub_blocks[bytes_counter+1]# update the subblocm size
    
    return ret_arr



# TODO: we skip the extensions for now instead of storing it 
def skip_extensions(bytes):
    
    skip_counter = 0
    
    # skip plain text extension
    
    
    # skip application extension
    
    
    
    # skip comment extension
    
    return skip_counter


with open('test.gif', 'rb') as f:
    bytez = f.read()
parseGIF(bytez)


class GIF:
    def __init__(self, size):
        pass
    
    
class Frame:
    def __init__(self):
        pass
    
    def parseFrame(self, bytez):
        pass
    
    
    
    
    
if __name__ == "__main__":
    GIF_FILENAME = "local_color.gif"
    # gif_lzw_decoding(GIF_FILENAME)
    visualize_frame(f"./framedata/{GIF_FILENAME}", f'frame0.txt', GIF_FILENAME)
    # filenames = get_filenames(f"./framedata/{GIF_FILENAME}/")
    # for filename in filenames:
    #     visualize_frame(f"./framedata/{GIF_FILENAME}", filename, GIF_FILENAME, output_format="file")
    
    
    
    
    
