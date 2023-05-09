from numpy.random import Generator
from randomgen import ChaCha

from data import GifData, GifFrame

ROUNDS = 12
def encrypt(gif:GifData, key, n = 100) -> GifData:
    
    # NOTE: seed the random generator with enc key
    rng = Generator(ChaCha(key=key, rounds=12))
    
    total_frames = len(gif.frames)
    
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
    from encode import GIF_encoder
    filename = "../dataset/sample-1.gif"
    from time import time
    
    gif_reader = GifReader(filename)
    gif = gif_reader.parse()
    
    # encrypt

    enc_key = 12121313876456
    print("About to encrypt!")
    encrypt(gif, enc_key, n = 100000)
    print("encrypt done!")
    
    encoder = GIF_encoder("output1.gif")
    from lzw_gif import compress
    print("About to encode!")
    encoder.encode(gif, compress)
    print("encode done!")
    encoder.to_file()
    

    print("Done!")