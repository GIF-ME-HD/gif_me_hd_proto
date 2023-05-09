from utils import get_sub_block_size, is_bit_set

EXTENSION_FACTORY_METHOD = {
        0xF9: lambda bytez: GraphicsControlExt(bytez),
        0xFE: lambda bytez: CommentExt(bytez),
        0xFF: lambda bytez: Extension(bytez),
        0x01: lambda bytez: Extension(bytez),
}


class Extension:
    def __init__(self, bytez):
        EXTENSION_INTRODUCER = 0x21
        SIZE_INDEX = 2
        self.bytez = bytez
        if self.bytez[0] != EXTENSION_INTRODUCER:
            raise Exception("Not a valid GIF Extension!")
        self.size = len(bytez)

    def validate_identifier(self, identifier, name):
        IDENTIFIER_INDEX = 1
        if self.bytez[IDENTIFIER_INDEX] != identifier:
            raise Exception(f"Not a {name}!")
    
    @staticmethod
    def is_extension(bytez, offset):
        if offset >= len(bytez):
            raise Exception("Invalid offset!")
        # all extension blocks begin with 0x21
        return bytez[offset] == 0x21
    
    @staticmethod
    def create_extension(bytez, offset):
        if offset+2 >= len(bytez):
            raise Exception("Invalid Extension index!")
        introducer = bytez[offset]
        ext_type = bytez[offset+1]
        
        size = get_sub_block_size(bytez, offset+2)
        print(f"Extension: {bytez[offset:offset+size+2]}")
        print(f"Ext Size: {size}")
        
        if introducer != 0x21:
            raise Exception("Not a valid GIF Extension!")

        new_bytez = bytez[offset:offset+size+2]
        print(f"3+15+1 = {len(new_bytez)}")
        return EXTENSION_FACTORY_METHOD[ext_type](new_bytez)

class GraphicsControlExt(Extension):
    def __init__(self, bytez):
        IDENTIFIER = 0xF9
        super().__init__(bytez)
        self.size = 8
        if len(bytez) != 8:
            raise Exception("Invalid Graphics Control size!")
        super().validate_identifier(IDENTIFIER, "Graphics Control Extension")

        packed = self.bytez[3]
        self.transparent_color_flag = is_bit_set(packed, 0)
        self.user_input_flag = is_bit_set(packed, 1)
        self.disposal_method = (packed & 0b000_111_00) >> 2
        self.delay_time = (self.bytez[5] << 8) | self.bytez[4] 
        self.transparent_color_index = self.bytez[6]
        print(f"Delay Time: {self.delay_time}")


class CommentExt(Extension):
    def __init__(self, bytez):
        IDENTIFIER = 0xFE
        super().__init__(bytez)
        self.size = bytez[2]+4
        super().validate_identifier(IDENTIFIER, "Comments Extension")
    
    def __repr__(self):
        return f"CommentExt({self.bytez})"

