from gif_stats import GifStatistics, FILENAMES




if __name__ == "__main__":
    stats = GifStatistics(N_lst=[10**i for i in range(4, 7)], password="pass", filenames=FILENAMES)
    
    stats.mse_stats()