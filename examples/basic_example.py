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

    # Create the reader object
    reader = GifReader(sample_gif)

    # Parse the image
    gif_image = reader.parse()

    # Print out various details about the GIF Image
    print(f"Loaded GIF {sample_gif}")
    print(f"GIF width: {gif_image.width}\tGIF height: {gif_image.height}")
    print(f"Number of frames: {len(gif_image.frames)}")
    print(f"Global Color Table Size: {len(gif_image.gct)}")
    print(f"First 10 RGB triplets in Global Color Table: {gif_image.gct[:10]}")


    gf = gif_image.frames[0]

    print(f"First frame info")
    print(f"Transparent Color Index: {gf.graphic_control.transparent_color_index}")
    print(f"Uses Local Color Table: {gf.img_descriptor.lct_flag}")
    print(f"Delay: {gf.graphic_control.delay_time*10} ms")
    list_of_indices = gf.frame_img_data
    print(f"First 10 indices in image: {gf.frame_img_data[:10]}")

    from gif_me_hd.encrypt import encrypt
    from gif_me_hd.encrypt import encrypt as decrypt
    n = 100000
    print("Encrypting Image...")
    encrypted_image = encrypt(gif_image, "password", n)
    print(f"Encrypted Image Info")
    print(f"First 10 RGB triplets in Global Color Table: {gif_image.gct[:10]}")

    from gif_me_hd.encode import GifEncoder
    encoder = GifEncoder("output_file.gif")
    encoder.encode(encrypted_image)
    encoder.to_file()
    # There should be a file called output_file.gif in your working directory now.
