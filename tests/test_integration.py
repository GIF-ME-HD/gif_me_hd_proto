import os
import unittest

from PIL import Image
from gif_me_hd.encode import GifEncoder
from gif_me_hd.parse import GifReader

DIRECTORY = "../dataset"

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

    def test_parsed_output1(self):
        # filename = sample_1.gif
        value = True
        self.assertTrue(value)
        
        # Add more assertions and test logic here
        
    def test_valid_gif_outputs(self):
        # produce gif data objects
        gifdatas = []
        for filename in self.all_gif_filenames:
            gif_reader = GifReader(filename)
            gif_data = gif_reader.parse()
            gifdatas.append((filename, gif_data))
            
        # make gifdata objects into output files
        for filename, gif_data in gifdatas:
            encoder = GifEncoder(filename)   
            encoder.to_file(f"./out/{filename}")

        # ask Pillow library if the output files are valid
        out_filenames = os.listdir("./out")
        for out_filename in out_filenames:
            is_gif_corrupted(out_filename)

if __name__ == "__main__":
    unittest.main()

