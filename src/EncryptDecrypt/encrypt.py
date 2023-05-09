from numpy.random import Generator
from randomgen import ChaCha

from ..data import GifData, GifFrame

ROUNDS = 12
def encrypt(gif:GifData, n, key) -> GifData:
    rng = Generator(ChaCha(key=key, rounds=12))
    total_frames = len(gif.frames)
    
    # Main perturbation
    for i in range(n):
        