from hashlib import scrypt
from numpy.random import Generator
from randomgen import ChaCha
from copy import deepcopy
from data import GifData, GifFrame

ROUNDS = 12

def encrypt(gif:GifData, password, n = 100) -> GifData:
    gif = deepcopy(gif)
    # NOTE: seed the random generator with enc key
    # TODO: future work, do not make the password the key directly
    rng = Generator(ChaCha(key=password2key(password, b""), rounds=ROUNDS))     # NOTE: now we asusme password is a integer
    
    total_frames = len(gif.frames)

    for _ in range(rng.integers(0, len(gif.gct) // 2)):
        idx = rng.integers(0, len(gif.gct))
        gif.gct[idx].r ^= rng.integers(0, 256)
        gif.gct[idx].g ^= rng.integers(0, 256)
        gif.gct[idx].b ^= rng.integers(0, 256)

    # do color pertubation for n times
    for i in range(n):        
        # get random frame
        frame = gif.frames[
            rng.integers(0, total_frames)]
        # get random pixel
        x = rng.integers(0, frame.img_descriptor.width)
        y = rng.integers(0, frame.img_descriptor.height)
        # pertubation
        color_perb = rng.integers(0, (2 ** (gif.gct_size+1)))   # exclusive of 256
        # apply pertubation
        apply_color_pertubation(gif, frame, x, y, color_perb)

    return gif


# TODO: do not use the password as the encryption key directly
def password2key(password, salt):
    # salt is a buffer of bytes (16 or more bytes)
    # password should be of sensisble length (<= 1024)
    ret = scrypt(password.encode(), salt=salt, n=4096, r=1, p=1)
    ret = int.from_bytes(ret[:32], byteorder="big")
    return ret

# TODO: store the salt in the gif 
def store_salt(filename): pass


def apply_color_pertubation(gif:GifData, frame:GifFrame, x, y, color_perb):
    access_index = y * frame.img_descriptor.width + x
    # get the index of the pixel to be mutated
    pixel_index = frame.frame_img_data[access_index] # map 2D to 1D
    # we have to make sure the mutated color index result is in the color table
    # TODO: check if a mod() is needed here to make sure it fits within the color table
    if frame.img_descriptor.lct_flag:
        pixel_index = pixel_index ^ color_perb # XOR
    elif gif.gct_flag: # use gct
        pixel_index = pixel_index ^ color_perb # XOR
    else:
        raise Exception("No color table found!")
    frame.frame_img_data[access_index] = pixel_index


if __name__ == "__main__":
    from parse import GifReader
    from encode import GifEncoder
    # filename = "../dataset/output1.gif"
    # filename = "../dataset/sample.gif"
    filename = "./output.gif"
    from time import time
    from lzw_gif import compress
    
    gif_reader = GifReader(filename)
    gif = gif_reader.parse()
    
    # encrypt
    enc_key = 12121313876456
    print("About to encrypt!")
    
    encrypted = encrypt(gif, enc_key, n = 100000)
    print("encrypt done!")
    
    # saving
    encoder = GifEncoder("decrypted.gif")
    print("About to encode!")
    encoder.encode(encrypted, compress)
    
    print("encode done!")
    encoder.to_file()
        
    print("Done!")