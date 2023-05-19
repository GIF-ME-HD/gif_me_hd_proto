import unittest
from gif_me_hd.encrypt import *
from gif_me_hd.parse import *

import os
import random
import string
import copy

DATASET = './test_dataset/'
class EncryptFunctionTester(unittest.TestCase):
    def test_pass2key_diffpass(self):
        # Test case 1
        # Different passwords with same salt provide different key
        salt = b'salt'
        letters = string.ascii_lowercase
        passwords = [''.join(random.choice(letters) for i in range(0,random.randint(5,100))) for _ in range(10000)]
        keys = set()
        for password in passwords:
            keys.add(password2key(password, salt))
        self.assertEqual(len(keys), len(passwords))

    def test_pass2key_diffsalt(self):
        # Test case 2
        # Diffent salts with same password
        password = 'password'
        salts = [random.randbytes(random.randint(5,100)) for _ in range(10000)]
        keys = set()
        for salt in salts:
            keys.add(password2key(password, salt))
        self.assertEqual(len(keys), len(salts))

class EncryptTester(unittest.TestCase):
    def setUp(self):
        self.filenames = os.listdir(DATASET)
        self.actual_path = [os.path.join(DATASET, x) for x in self.filenames]
        self.gifs = [GifReader(x).parse() for x in self.actual_path]

    def test_perturbation_change_color_table(self):
        # Test case 3
        # Pertubation of color table
        from numpy.random import Generator
        from randomgen import ChaCha
        from gif_me_hd.data import GifData, RGB
        import random
        random.seed(42)

        rng = Generator(ChaCha(key=314159265, rounds=2))
        sample_gif = GifData()

        old_color_table = [RGB(random.randint(0,255),random.randint(0, 255), random.randint(0, 255)) for _ in range(256)]
        sample_gif.gct = copy.deepcopy(old_color_table)

        color_table_pertubation(sample_gif, rng)
        # print(sample_gif.gct)
        # print(old_color_table)
        self.assertNotEqual(sample_gif.gct, old_color_table)


    def test_perturbation_change_indices(self):
        # Test case 4
        # Pertubation of pixel indices 
        from numpy.random import Generator
        from randomgen import ChaCha
        from gif_me_hd.data import GifData, GifFrame, ImageDescriptor, RGB

        import random
        random.seed(42)

        rng = Generator(ChaCha(key=314159265, rounds=2))
        sample_gif = GifData()

        old_color_table = [RGB(random.randint(0,255),random.randint(0, 255), random.randint(0, 255)) for _ in range(256)]
        sample_gif.gct = copy.deepcopy(old_color_table)
        sample_gif.gct_flag = True
        sample_gif.gct_size = 7

        id = ImageDescriptor()
        id.width = 8
        id.height = 8
        old_indices = [random.randint(0,100) for _ in range(id.width*id.height)]

        gf = GifFrame()
        gf.frame_img_data = copy.deepcopy(old_indices)
        gf.img_descriptor = id

        sample_gif.frames.append(gf) 

        indices_data_pertubation(sample_gif, 1000, len(sample_gif.frames), rng)
        # print(sample_gif.frames[0].frame_img_data)
        # print(old_indices)
        self.assertNotEqual(sample_gif.frames[0].frame_img_data, old_indices)

    def test_perturbation_change_image(self):
        # Test case 5
        # Pertubation from image encrytion
        for gif_image in self.gifs:
            old_frame_lst = gif_image.frames[0].frame_img_data[:]
            old_color_table = copy.deepcopy(gif_image.gct)
            encrypted_image = encrypt(gif_image, "password123", 100000)
            self.assertNotEqual(encrypted_image.frames[0].frame_img_data,
                                old_frame_lst)
            self.assertNotEqual(encrypted_image.gct, old_color_table)


if __name__ == "__main__":
    unittest.main()

