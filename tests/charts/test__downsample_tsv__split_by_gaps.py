import unittest
from examples.charts.downsample_tsv import GAP_VALUE, split_by_gaps

DATETIME = list(map(lambda x: '2000-01-01T00:00:' + str(x).zfill(2) + 'Z', range(6)))
VALUE = list(map(lambda x: 100.0 + float(x), range(6)))


class DownsampleTSV_SplitByGaps_Tests(unittest.TestCase):
    def test_no_split_when_no_gaps(self):
        data = [[DATETIME[0], VALUE[0]],
                [DATETIME[1], VALUE[1]],
                [DATETIME[2], VALUE[2]],
                [DATETIME[3], VALUE[3]],
                [DATETIME[4], VALUE[4]],
                [DATETIME[5], VALUE[5]]]

        result = _split_by_gaps(data)

        self.assertEqual(result, [data])

    def test_split_by_single_gap(self):
        data = [[DATETIME[0], VALUE[0]],
                [DATETIME[1], VALUE[1]],
                [DATETIME[2], GAP_VALUE],
                [DATETIME[3], VALUE[3]],
                [DATETIME[4], VALUE[4]],
                [DATETIME[5], VALUE[5]]]

        result = _split_by_gaps(data)

        self.assertEqual(result, [[[DATETIME[0], VALUE[0]],
                                   [DATETIME[1], VALUE[1]]],
                                  [[DATETIME[2], GAP_VALUE]],
                                  [[DATETIME[3], VALUE[3]],
                                   [DATETIME[4], VALUE[4]],
                                   [DATETIME[5], VALUE[5]]]])

    def test_split_by_repeated_gaps_(self):
        data = [[DATETIME[0], VALUE[0]],
                [DATETIME[1], VALUE[1]],
                [DATETIME[2], GAP_VALUE],
                [DATETIME[3], VALUE[3]],
                [DATETIME[4], VALUE[4]],
                [DATETIME[5], VALUE[5]]]

        result = _split_by_gaps(data)

        self.assertEqual(result, [[[DATETIME[0], VALUE[0]],
                                   [DATETIME[1], VALUE[1]]],
                                  [[DATETIME[2], GAP_VALUE]],
                                  [[DATETIME[3], VALUE[3]],
                                   [DATETIME[4], VALUE[4]],
                                   [DATETIME[5], VALUE[5]]]])

    def test_preserve_first_gap(self):
        data = [[DATETIME[0], GAP_VALUE],
                [DATETIME[1], VALUE[1]],
                [DATETIME[2], VALUE[2]],
                [DATETIME[3], VALUE[3]],
                [DATETIME[4], VALUE[4]],
                [DATETIME[5], VALUE[5]]]

        result = _split_by_gaps(data)

        self.assertEqual(result, [[[DATETIME[0], GAP_VALUE]],
                                  [[DATETIME[1], VALUE[1]],
                                   [DATETIME[2], VALUE[2]],
                                   [DATETIME[3], VALUE[3]],
                                   [DATETIME[4], VALUE[4]],
                                   [DATETIME[5], VALUE[5]]]])

    def test_preserve_last_gap(self):
        data = [[DATETIME[0], VALUE[0]],
                [DATETIME[1], VALUE[1]],
                [DATETIME[2], VALUE[2]],
                [DATETIME[3], VALUE[3]],
                [DATETIME[4], VALUE[4]],
                [DATETIME[5], GAP_VALUE]]

        result = _split_by_gaps(data)

        self.assertEqual(result, [[[DATETIME[0], VALUE[0]],
                                   [DATETIME[1], VALUE[1]],
                                   [DATETIME[2], VALUE[2]],
                                   [DATETIME[3], VALUE[3]],
                                   [DATETIME[4], VALUE[4]]],
                                  [[DATETIME[5], GAP_VALUE]]])

    def test_preserve_the_only_gap(self):
        data = [[DATETIME[0], GAP_VALUE]]

        result = _split_by_gaps(data)

        self.assertEqual(result, [[[DATETIME[0], GAP_VALUE]]])


def _split_by_gaps(series):
    return split_by_gaps(lambda datetime_value: datetime_value[1] == GAP_VALUE, series)


if __name__ == '__main__':
    unittest.main()
