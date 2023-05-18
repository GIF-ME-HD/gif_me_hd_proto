import copy
import os
import unittest
import numpy as np
import matplotlib.pyplot as plt

from gif_me_hd.parse import GifReader
from gif_me_hd.data import GifData, GifFrame, RGB
from gif_me_hd.encrypt import encrypt
from gif_me_hd.encode import GifEncoder


class FileStatistics():
    def __init__(self) -> None:
        pass

    def get_uniformity_graph(self, filename):
        # if the file exists
        if os.path.isfile(filename):
            gif_reader = GifReader(filename)
            orig_gif_data = gif_reader.parse()
            
            indices = []
            for frame in orig_gif_data.frames:
                indices += frame.frame_img_data

            fig, ax = plt.subplots()
            ax.hist(np.array(indices), bins = [_ for _ in range(1+max(indices))])

            plt.title(filename + " - ORIG")
            plt.show()

            orig_indices = indices[:]
            indices = []
            encrypted_gif = encrypt(orig_gif_data, "password123", 1000000)
            encoder = GifEncoder("test_encrypted.gif")
            encoder.encode(encrypted_gif)
            encoder.to_file()

            for frame in encrypted_gif.frames:
                indices += frame.frame_img_data


            fig, ax = plt.subplots()
            ax.hist(np.array(indices), bins = [_ for _ in range(1+max(indices))])
            plt.title(filename + " - ENCRYPTED")
            plt.show()



        else:
            raise FileNotFoundError

    
    def get_filesize(self, file_path, unit="kb") -> int:
        # if the file exists
        if os.path.isfile(file_path):
            # get file size in bytes
            file_size = os.path.getsize(file_path)
            # bytes to kilobytes (optional)
            file_size_kb = file_size / 1024
            print(f"File size: {file_size} bytes ({file_size_kb} KB)")
            if unit == "bytes":
                return file_size
            elif unit == "kb":
                return file_size / 1024
            elif unit == "mb":
                return file_size_kb / (1024**2)
        else:
            raise FileNotFoundError

    def mutated_pixel_stats(self, gif_filenames):
        def count_mutated_pixels(gif: GifData, encrypted: GifData):
            """
            Counts the total number of mutated pixels in a GifData, given the GCT or the LCT if it exists
            """
            mutated_pixel_count = 0
            # count the number of pixels that wasn't in original lct
            # loop through all frames
            color_table = None
            for i in range(len(gif.frames)):
                ori_frame = gif.frames[i]
                enc_frame = encrypted.frames[i]
                frame_mutated_count = 0
                # loop thru each pixel
                for j in range(len(ori_frame.frame_img_data)):
                    # NOTE: there is mutation IF : 1. the currnet pixel color index doesnt match the original unecrypted frame color index
                    if ori_frame.frame_img_data[j] != enc_frame.frame_img_data[j]:
                        frame_mutated_count += 1
                mutated_pixel_count += frame_mutated_count
            return mutated_pixel_count
        
        def plot(all_stats, N_lst):
            # Sample data
            # mutated_pixel_count = [10, 15, 20, 25, 30]  # Example values for mutated pixel count
            # file_size = [100, 200, 300, 400, 500]  # Example values for file size
            
            # Plotting the graph
            # plt.plot(N_lst, mutated_pixel_count, marker='o', label='Mutated Pixel Count')
            for filename, gif_data, file_stats in all_stats:
                # plotting: N_lst, mutated_pixel_count
                plt.plot(N_lst, [_[1] for _ in file_stats], marker='o', label=filename)
            # plt.plot(N_lst, file_size, marker='o', label='File Size')
            plt.xlabel('N')
            plt.ylabel('Count/File Size')
            plt.title('Mutated Pixel Count vs N vs File Size')
            plt.legend()
            plt.grid(True)
            plt.show()
    

        # open each file and parse into GifData object
        gifdatas = []
        for filename in gif_filenames:
            gif_reader = GifReader(filename)
            gif_data = gif_reader.parse()
            gifdatas.append((filename, gif_data))

        # NOTE: calculate statistics for each giffile
        all_stats = []
        N_lst = [10**i for i in range(4, 7)]
        # loop through every pre-encrypted gifdata
        for filename, gif_data in gifdatas:
            file_stats = []
            # vary N (10^4 to 10^8)
            for N in N_lst:
                # encrypt the copy of gifdata
                copied = copy.deepcopy(gif_data)
                encrypted = encrypt(copied, "pass", n=N)
                # count the number of mutated pixels
                mutated_pixel_count = count_mutated_pixels(gif_data, encrypted)
                # store the statistics
                file_stats.append((N, mutated_pixel_count))
                
            all_stats.append((filename, gif_data, file_stats))
        
        print(all_stats)
        # TODO: plotting
        plot(all_stats, N_lst)
        

    # TODO: comparison between mean squared error, PSNR, N 
    def mse_stats(self):
        """
        Mean Squared Error (MSE) is the most commonly used image quality metric.
        """
        
        # NOTE: MSE = (1/N) * Σ[(xi - yi)^2]
        def compute_mse(ori: GifData, encrypted: GifData):
            # loop each frame of original and encrypted
            pixel_count = 0
            squared_differences = 0
            for i in range(len(ori.frames)):
                ori_frame = ori.frames[i]
                enc_frame = encrypted.frames[i]
                
                # loop through each pixel of each frame
                for j in range(len(ori_frame.frame_img_data)):
                    ori_pixel = ori_frame.frame_img_data[j]
                    enc_pixel = enc_frame.frame_img_data[j]
                    # compute the sqaured diff
                    squared_differences += (ori_pixel - enc_pixel)**2
                    pixel_count += 1
            
            mse = (1/pixel_count) * squared_differences
            return mse
        
        # TODO: the function to compute the PSNR of a gif
        # TOASK: not sure whether higher is btetter?
        def compute_PSNR():
            pass
        
        def plot(filenames, N_lst, mse_lst):
            # Sample data            
            # Plotting the graph
            for filename in filenames:
                plt.plot(N_lst, mse_lst, marker='o', label=filename)
            
            plt.xlabel('N')
            plt.ylabel('Count/File Size')
            plt.title('Mutated Pixel Count vs N vs File Size')
            plt.legend()
            plt.grid(True)
            plt.show()
    



if __name__ == "__main__":
    # statistics of m
    stats = FileStatistics()
    filenames = ["../dataset/sample_1.gif", "../dataset/sample-1.gif", "../dataset/esqueleto.gif"]
    for file in filenames:
        stats.get_uniformity_graph(file)

    stats.mutated_pixel_stats(filenames)

