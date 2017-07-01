import unittest
from datetime import datetime as dt
# import ..src/downsample.py

class Downsample_parseDateTime_Tests(unittest.TestCase):

    def test_normalize_offset(self):
        # parse_datetime("")
        self.assertEqual('foo'.upper(), 'FOO')

if __name__ == '__main__':
    unittest.main()