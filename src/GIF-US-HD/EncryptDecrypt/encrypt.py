from numpy.random import Generator
from randomgen import ChaCha

from ..data import GifData, GifFrame

ROUNDS = 12
def encrypt(gif:GifData, n, key):
    rng = Generator(ChaCha(key=key, rounds=12))
    for i in range(n):
        pass