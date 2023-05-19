import unittest
from gif_me_hd.encrypt import *

import random
import string


class EncryptTester(unittest.TestCase):
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

if __name__ == "__main__":
    unittest.main()

