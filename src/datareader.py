import struct
from data import RGB

class DataReader:
    def __init__(self, filename, offset=0):
        with open(filename, "rb") as f:
            self.bytez = f.read()
        self.length = len(self.bytez)
        self.offset = offset
    
    def is_done(self):
        return self.offset >= self.length

    def advance(self, i):
        self.offset += i
        self.check(0)
    
    def peek_byte(self, offset=0):
        self.check(1)
        ret = ord(struct.unpack_from("<c",
               self.bytez, offset=self.offset)[0])
        return ret

    def read_byte(self):
        ret =  self.peek_byte()
        self.advance(1)
        return ret

    def read_triplet(self):
        r = self.read_byte()
        g = self.read_byte()
        b = self.read_byte()
        return RGB(r, g, b)

    def read_triplet_list(self, num):
        ret = []
        for _ in range(num):
            ret.append(self.read_triplet())
        return ret

    def read_byte_list(self, num):
        ret = []
        for _ in range(num):
            ret.append(self.read_byte())
        return ret
    
    def read_short(self):
        self.check(2)
        ret = struct.unpack_from("<h", self.bytez, offset=self.offset)[0]
        self.advance(2)
        return ret

    def check(self, offset):
        if self.offset + offset <= self.length:
            return True
        else:
            raise Exception("Cannot access value at offset " +
           str(self.offset+offset))