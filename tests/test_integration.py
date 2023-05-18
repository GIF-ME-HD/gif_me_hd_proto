import os
import unittest

from PIL import Image
from gif_me_hd.encode import GifEncoder
from gif_me_hd.parse import GifReader
from lzw_gif_cpp import compress

DIRECTORY = "../dataset/"

def is_gif_corrupted(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify()
        return False
    except (IOError, SyntaxError):
        return True


class IntegrationTest(unittest.TestCase):
    def setUp(self):
        # Get all filenames in the directory
        filenames = os.listdir(DIRECTORY)
        # Filter filenames ending with .gif
        self.all_gif_filenames = [filename for filename in filenames if filename.endswith('.gif')]
        # produce gif data objects
        self.gifdatas = []
        for filename in self.all_gif_filenames:
            try:
                gif_reader = GifReader(f"{DIRECTORY}{filename}")
                gif_data = gif_reader.parse()
                self.gifdatas.append((filename, gif_data))
            # 87a header
            except Exception as e:
                print(f" 87a header detected in {filename}")

        
    def test_valid_gif_outputs(self):
            
        # make gifdata objects into output files
        if (not os.path.exists("./out/")):
            os.mkdir("./out/")
        
        for filename, gif_data in self.gifdatas:
            # output file directory
            encoder = GifEncoder(f"./out/out_{filename}")  
            encoder.encode(gif_data, compress) 
            encoder.to_file()

        # ask Pillow library if the output files are valid
        out_filenames = os.listdir("./out/")
        for out_filename in out_filenames:
            is_gif_corrupted(out_filename)

        # remove all the files in ./out/
        # Remove all files within the directory
        for filename in out_filenames:
            if os.path.isfile(f"./out/{filename}"):
                os.remove(f"./out/{filename}")
        os.rmdir("./out/")
        

if __name__ == "__main__":
    unittest.main()

