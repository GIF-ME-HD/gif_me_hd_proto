import unittest
import copy
import os
import unittest
from matplotlib import ticker
import matplotlib.pyplot as plt

from gif_me_hd.parse import GifReader
from gif_me_hd.data import GifData, GifFrame, RGB
from gif_me_hd.encrypt import encrypt
from lzw_gif_cpp import compress
from PIL import Image

DIRECTORY = "../dataset"

def load_pillow_img_files(filenames):
    img_objs = []
    for filename in filenames:
        try:
            img = Image.open(f"{filename}")
            img_objs.append(img)
        except (IOError, SyntaxError):
            print(f"Corrupted file: {filename}")
    return img_objs


def close_pillow_img_files(img_objs):
    [img.close() for img in img_objs]

class DecoderTester(unittest.TestCase):
    def setUp(self) -> None:
        # Get all filenames in the directory
        filenames = os.listdir(DIRECTORY)
        # Filter filenames ending with .gif
        self.all_gif_filenames = [filename for filename in filenames if filename.endswith('.gif')]
        # produce gif data objects
        self.gif_file_datas = []
        for filename in self.all_gif_filenames:
            try:
                gif_reader = GifReader(f"{DIRECTORY}/{filename}")
                gif_data = gif_reader.parse()
                self.gif_file_datas.append((filename, gif_data))
            # 87a header
            except Exception as e:
                print(f" 87a header detected in {filename}")
        self.assertTrue(True)

    # def test_dimensions(self):
    #     """" testing canvas dimensions of the gifdata compared against pillow """

    #     dimensions = []
    #     for filename, gif_data in self.gif_file_datas:
    #         # get the dimensions of the gif using pillow
    #         with Image.open(f"{DIRECTORY}/{filename}") as img:      
    #             dimensions.append((img.width, img.height))
            
    #     for i in range(len(self.gif_file_datas)):
    #         gif = self.gif_file_datas[i][1]
    #         self.assertEqual(dimensions[i][0], gif.width)
    #         self.assertEqual(dimensions[i][1], gif.height)

    # def test_color_table(self):
    #     """" color table against pillow image library """
    #     print(f"\n color table against pillow image library\n ")
    #     def is_subset_of(lst1, lst2):
    #         # check if lst1 is a subset of lst2
    #         for e1 in lst1:
    #             if e1 not in lst2:
    #                 print(f"e1: {e1} not in lst2: {lst2}")
    #                 return False
    #         return True
        
    #     pillow_img_files = load_pillow_img_files([f"{DIRECTORY}/{gif_file_datas[0]}" for gif_file_datas in self.gif_file_datas])
        
    #     # get GifData GCT
    #     gcts = [gif_file_data[1].gct for gif_file_data in self.gif_file_datas]
        
    #     # get the GCT using pillow
    #     pillow_gcts = []
    #     for img in pillow_img_files:
    #         pallette = img.getpalette()
    #         gct = [RGB(pallette[i], pallette[i+1], pallette[i+2]) for i in range(0, len(pallette), 3)]
    #         print(f"gct: {gct}")
    #         pillow_gcts.append(gct)
        
    #     close_pillow_img_files(pillow_img_files)
        
    #     assert(len(pillow_gcts) == len(gcts))

    #     for i in range(len(gcts)):
    #         self.assertTrue(is_subset_of(pillow_gcts[i], gcts[i])) 


    def test_malformed_gif_header(self):
        """ testing for malformed gif header """
        # NOTE: assumes there is a malformed gif header in the dataset already
        print(f"\n testing for malformed gif header \n ")

        # loop through each gif file ion malformed directory
        malformed_filenames = os.listdir(f"{DIRECTORY}/malformed_header/")
        malformed_filenames = [filename for filename in malformed_filenames if filename.endswith('.gif')]
        print(f"malformed_filenames: {malformed_filenames}")
        for name in malformed_filenames:
            malformed = False
            try:
                reader = GifReader(f"{DIRECTORY}/malformed_header/{name}.gif")
                gif = reader.parse()
            except Exception as e:
                print(f"Exception: {e}")
                malformed = True
            finally:
                self.assertTrue(malformed)
        
    # # TODO:
    def test_valid_extensions(self):
        """ testing for malformed gif header """

        pass
    
    
    
    # # TODO: malform the file extensions
    def test_malformed_extensions(self):
        """ testing for malformed extensions """

        pass
    
    
    
    
    
if __name__ == "__main__":
    unittest.main()

