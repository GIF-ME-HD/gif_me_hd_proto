import copy
import os
import unittest
from matplotlib import ticker
import matplotlib.pyplot as plt

from gif_me_hd.parse import GifReader
from gif_me_hd.data import GifData, GifFrame, RGB
from gif_me_hd.encrypt import encrypt
from lzw_gif_cpp import compress


FILENAMES = ["../dataset/sample_1.gif", "../dataset/sample-1.gif", "../dataset/esqueleto.gif"]

class GifStatistics():
    def __init__(self, N_lst, password, filenames=FILENAMES) -> None:
        # load all the filenames into GifData objects
        self.filenames = filenames
        self.gifdatas = [GifReader(filename).parse() for filename in filenames]
        # encrypting gifdata
        self.encrypted_gifdatas = []
        for gifdata in self.gifdatas:
            temp = []
            for n in N_lst:
                copied = copy.deepcopy(gifdata)
                encrypted = encrypt(copied, password, n=n)
                temp.append((encrypted, n))
            self.encrypted_gifdatas.append(temp)
        print(f"encrypted_gifdatas: {self.encrypted_gifdatas}")
        assert(len(self.gifdatas) == len(self.encrypted_gifdatas) == len(filenames))
        print(f"how many gif datas? {len(self.gifdatas)}")
        
        self.N_lst = N_lst
        self.password = password
        
    
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
                return file_size / (1024**2)
        else:
            raise FileNotFoundError
        
    def get_pixel_count(gif: GifData):
        total = 0
        for i in range(len(gif.frames)):
            frame = gif.frames[i]
            for j in range(len(frame.frame_img_data)):
                total+=1
        return total

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
        
        # TODO: plot all of the gif files instead of a select few
        # TODO: plot out the file size for comparison as well
        def plot(all_stats, N_lst):
            print(f"all_stats: {all_stats}")
            keyfunc = lambda stat, gif: stat[1] / GifStatistics.get_pixel_count(gif)# this is the normalized mutated pixel count (mutated pixel count / total pixels)
            
            # loop through each gif's statistics
            for filename, gif_data, file_stats in all_stats:
                # plotting: N_lst, mutated_pixel_count
                plt.plot(N_lst, [keyfunc(stat, gif_data) for stat in file_stats], marker='o', label=filename)
            
            # plt.plot(N_lst, file_size, marker='o', label='File Size')
            plt.xlabel('N')
            # plt.gca().xaxis.set_major_locator(ticker.FixedLocator(N_lst))
            # plt.gca().xaxis.set_major_formatter(ticker.FixedFormatter(["A", "B", "C"]))

            plt.ylabel('Mutated Pixel Ratio')
            plt.title('Mutated Pixel Count Ratio vs N for different GIFs')
            plt.legend()
            plt.grid(True)
            plt.show()



        # NOTE: calculate statistics for each giffile
        all_stats = []
        
        # TODO: clean up to remove encrypt here
        # loop through every pre-encrypted gifdata
        for i in range(len(self.gifdatas)) :
            file_stats = []
            # vary N (10^4 to 10^8)
            for j in range(len(self.N_lst)):
                mutated_pixel_count = count_mutated_pixels(self.gifdatas[i], self.encrypted_gifdatas[i][j][0])
                # store the statistics
                file_stats.append((self.N_lst[j], mutated_pixel_count))
                
            all_stats.append((self.filenames[i], self.gifdatas[i], file_stats))
        
        print(f"all_stats: {all_stats}")
        # TODO: plotting
        plot(all_stats, self.N_lst)
        

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
        
        def plot(filenames, N_lst, mse_stats):
            # Sample data            
            # Plotting the graph
            for i in range(len(self.filenames)):
                plt.plot(N_lst, [mse for N,mse in mse_stats[i]], marker='o', label=filenames[i])
            
            plt.xlabel('N')
            plt.ylabel('Mean Squared Error')
            plt.title('Mutated Pixel Count vs N vs File Size')
            plt.legend()
            plt.grid(True)
            plt.show()
            
        # compute_mse for each gif
        mse_stats = []
        for i in range(len(self.gifdatas)):       
            temp = []     
            for (encrypted, N) in self.encrypted_gifdatas[i]:
                mse = compute_mse(self.gifdatas[i], encrypted)
                temp.append((N, mse))
            mse_stats.append(temp)
            # [[(12.12121, 10), (12.12121, 10)], [(12.12121, 10), (12.12121, 10)]]
        print(f"mse_stats: {mse_stats}")
        # plot
        plot(self.filenames, self.N_lst, mse_stats)

if __name__ == "__main__":
    # statistics of 
    filenames = ["../dataset/sample_1.gif", "../dataset/sample-1.gif", "../dataset/esqueleto.gif"]
    stats = GifStatistics(N_lst=[10**i for i in range(4, 7)], password="pass", filenames=FILENAMES)
    stats.mutated_pixel_stats(gif_filenames=FILENAMES)
    # stats.mse_stats(filenames)
