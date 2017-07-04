import unittest
from examples.downsample_tsv import parse_datetime


class DownsampleTSV_ParseDateTime_Tests(unittest.TestCase):
    def test_parse_regular(self):
        datetime = parse_datetime('2000-10-20T03:40:50.6001+07:08')
        self.assertEqual(datetime.strftime('%Y-%m-%d %H:%M:%S.%f%z'), '2000-10-20 03:40:50.600100+0708')

    def test_parse_absent_microseconds(self):
        datetime = parse_datetime('2000-10-20T03:40:50+07:08')
        self.assertEqual(datetime.strftime('%Y-%m-%d %H:%M:%S.%f%z'), '2000-10-20 03:40:50.000000+0708')

    def test_parse_Z_offset(self):
        datetime = parse_datetime('2000-10-20T03:40:50.6001Z')
        self.assertEqual(datetime.strftime('%Y-%m-%d %H:%M:%S.%f%z'), '2000-10-20 03:40:50.600100+0000')


if __name__ == '__main__':
    unittest.main()
