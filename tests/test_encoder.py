import unittest

import os
from gif_me_hd.parse import *
from gif_me_hd.encode import *
from lzw_gif_cpp import compress

DATASET = './dataset/'


class EncoderTester(unittest.TestCase):
    def setUp(self):
        self.filenames = os.listdir(DATASET)
        self.actual_path = [os.path.join(DATASET, x) for x in self.filenames]
        self.gifs = [GifReader(x).parse() for x in self.actual_path]

    def test_saved_reparsed_gif(self):
        # Test case 1+2
        # Save the GIF files
        test_dir = 'output/'
        os.makedirs(test_dir,exist_ok=True)
        for index, gif in enumerate(self.gifs):
            encoder = GifEncoder(os.path.join(
                test_dir, f'encoded_{self.filenames[index]}'))
            encoder.encode(gif, compress)
            encoder.to_file()
        # Reparse the saved files
        self.parsed_gifs = [GifReader(os.path.join(
            test_dir, f'encoded_{filename}')).parse() for filename in self.filenames]
        
        # Re-save parsed
        for index, gif in enumerate(self.parsed_gifs):
            encoder = GifEncoder(os.path.join(
                test_dir, f're-encoded_{self.filenames[index]}'))
            encoder.encode(gif, compress)
            encoder.to_file()


if __name__ == "__main__":
    unittest.main()
