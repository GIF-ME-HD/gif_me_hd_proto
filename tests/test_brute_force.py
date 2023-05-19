#!/usr/bin/env python
from gif_me_hd.parse import GifReader
import random
import copy
from gif_me_hd.encrypt import encrypt_raw_key
from gif_me_hd.encrypt import encrypt_raw_key as decrypt_raw_key

random.seed(31415926)

def brute_force(original_gif, encrypted_gif, n):
    key = 0
    new_decrypted = copy.deepcopy(encrypted_gif)
    while True:
        decrypt_raw_key(new_decrypted, key, n)
    
        if new_decrypted.frames[0].frame_img_data == original_gif.frames[0].frame_img_data:
            return key
        decrypt_raw_key(new_decrypted, key, n)
        key += 1

if __name__ == '__main__':
    # Download GIF
    def download_gif(url, filename):
        import requests
        req = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0'})
        with open(filename, 'wb') as f:
            f.write(req.content)

    sample_gif = 'sample_gif.gif'
    download_gif('https://www.matthewflickinger.com/lab/whatsinagif/images/sample_1.gif', sample_gif)

    # Create the reader object
    reader = GifReader(sample_gif)

    # Parse the image
    gif_image = reader.parse()
    original_gif_image = copy.deepcopy(gif_image)

    n = 100

    import time
    for key_range in [(0, 101), (100, 1001), (1000, 10001), (10000, 100001)]:
        start = time.time()
        print(f"Encrypting Image where key is number between {key_range[0]} and {key_range[1]-1}")
        encrypt_raw_key(gif_image, random.randint(*key_range), n)
        encrypted_gif = gif_image
        key = brute_force(encrypted_gif, original_gif_image, n)
        end = time.time()
        print(f"Found key for Image! It is {key}! Time Taken: {end-start}s")
        decrypt_raw_key(gif_image, key, n)

