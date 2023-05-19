import unittest

import os

from gif_me_hd.parse import GifReader
from gif_me_hd.data import GifData
from gif_me_hd.encrypt import encrypt
from gif_me_hd.encode import GifEncoder


DATASET = './dataset/'


class BlackBoxTester(unittest.TestCase):
    def setUp(self):
        self.filenames = [x for x in os.listdir(
            DATASET) if os.path.isfile(os.path.join(DATASET, x))]
        self.actual_path = [os.path.join(DATASET, x) for x in self.filenames]

    def test_parsing_gif(self):
        # Test case 1
        try:
            for path in self.actual_path:
                GifReader(path).parse()
        except Exception:
            self.fail("Parsing Unexpectedly fails.")

    def test_parsing_nongif(self):
        def func(path):
            GifReader(path).parse()
        # Test case 2
        invalid_files = [os.path.join(DATASET, 'random_files', x) for x in os.listdir(
            os.path.join(DATASET, 'random_files'))]
        for path in invalid_files:
            self.assertRaises(Exception, func, path)

    def test_encrypt_empty(self):
        import random
        import string
        def func(password, n):
            encrypt(GifData(), password, n)
        passwords = [''.join(random.choice(string.ascii_letters) for i in range(
            0, random.randint(5, 100))) for _ in range(10000)]
        for password in passwords:
            self.assertRaises(Exception, func, password, 10000)

    def test_encode_manual_change(self):
        for index, path in enumerate(self.actual_path):
            parsed_gif = GifReader(path).parse()
            parsed_gif.frames[0].frame_img_data = [0]*len(parsed_gif.frames[0].frame_img_data)
            encoder = GifEncoder(f'{index}.gif')
            encoder.encode(parsed_gif)
            encoder.to_file()

if __name__ == "__main__":
    unittest.main()
