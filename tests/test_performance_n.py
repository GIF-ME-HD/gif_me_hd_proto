#!/usr/bin/env python
from gif_me_hd.parse import GifReader

if __name__ == '__main__':
    # Download GIF
    def download_gif(url, filename):
        import requests
        req = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(req.content)

    sample_gif = 'sample_gif.gif'
    download_gif('https://media.tenor.com/eupJDAG479cAAAAC/infinity-train-dance.gif', sample_gif)

    from gif_me_hd.encrypt import encrypt
    from gif_me_hd.encrypt import encrypt as decrypt
    import math

    n_vals = [10 ** 100000, 10 ** 1000000]
    print("Done calculating exponentiations")
    import time
    for n in n_vals:
        start = time.time()
        # Create the reader object
        reader = GifReader(sample_gif)

        # Parse the image
        gif_image = reader.parse()

        exponent =int(math.ceil(math.log(n,10)))
        encrypt(gif_image, "password", n)

        from gif_me_hd.encode import GifEncoder
        encoder = GifEncoder("output_file.gif")
        encoder.encode(gif_image)
        encoder.to_file()

        end = time.time()
        print(f"For value n=10 ** {exponent} and file `infinity-train-dance.gif`, took {end-start} seconds for whole process")
