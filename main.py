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


with open('test.gif', 'rb') as f:
    bytez = f.read()
parseGIF(bytez)

class GIF:
    def __init__(self, size):
        pass

class Frame:
    def __init__(self):
        pass