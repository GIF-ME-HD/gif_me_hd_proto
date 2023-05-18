from copy import deepcopy
from ..data import GifData, GifFrame

class GifDataHider:
    def __init__(self, gif_original:GifData):
        self.gif_original = gif_original
        self.gif = deepcopy(gif_original)
    
    