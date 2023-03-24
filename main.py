import struct
HEADER = b'\x47\x49\x46\x38\x39\x61' #GIF89a

def parseGIF(bytez):

    # HEADER Block (Byte 0 -> 5)
    # Verify is GIF + Right Version
    if not bytez.startswith(HEADER):
        print('This is not a GIF89a compliant GIF File!')
        return None
    

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
    
    # TODO Image Descriptor & Frame
    # Image Descriptor & Each Frame
    # For amount of frames, parse image descriptor for frame and frame data

    
    
# needs to add a code for each color in the color table
def build_lzw_codetable(colortable):
    # build the code table
    pass
    
def gif_lzw_decoding():
    # initialize code table
    
    
    
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
    
    
    




    

