import unittest
from examples.downsample_tsv import GAP_VALUE, distribute_points_among_series_parts

DATETIME = list(map(lambda x: '2000-01-01T00:' + str(x).zfill(2) + ':00Z', range(11)))
VALUE = list(map(lambda x: 100.0 + float(x), range(11)))


class DownsampleTSV_DistributePointsAmongSeriesParts_Tests(unittest.TestCase):
    def test_no_parts(self):
        data = []

        result = _distribute_points_among_series_parts(5, data)

        self.assertEqual(result, [])

    def test_single_empty_part(self):
        data = [[]]

        result = _distribute_points_among_series_parts(5, data)

        self.assertEqual(result, [series_part(0, 0, data[0])])

    def test_single_part_with_gap(self):
        data = [[[DATETIME[0], GAP_VALUE]]]

        result = _distribute_points_among_series_parts(5, data)

        self.assertEqual(result, [series_part(1, 0, data[0])])

    def test_single_part_with_single_item(self):
        data = [[[DATETIME[0], VALUE[0]]]]

        result = _distribute_points_among_series_parts(5, data)

        self.assertEqual(result, [series_part(1, 0, data[0])])

    def test_single_part(self):
        data = [[[DATETIME[0], VALUE[0]],
                 [DATETIME[1], VALUE[1]],
                 [DATETIME[2], VALUE[2]],
                 [DATETIME[3], VALUE[3]],
                 [DATETIME[4], VALUE[4]],
                 [DATETIME[5], VALUE[5]]]]

        result = _distribute_points_among_series_parts(5, data)

        self.assertEqual(result, [series_part(2, 3, data[0])])

    def test_num_points_to_distribute_is_less_than_num_bound_points(self):
        data = [[[DATETIME[0], VALUE[0]],
                 [DATETIME[1], VALUE[1]],
                 [DATETIME[2], VALUE[2]]],
                [[DATETIME[3], GAP_VALUE]],
                [[DATETIME[4], VALUE[4]],
                 [DATETIME[5], VALUE[5]]]]

        result = _distribute_points_among_series_parts(4, data)

        self.assertEqual(result, [series_part(2, 0, data[0]), series_part(1, 0, data[1]), series_part(2, 0, data[2])])

    def test_num_points_to_distribute_is_equal_num_bound_points(self):
        data = [[[DATETIME[0], VALUE[0]],
                 [DATETIME[1], VALUE[1]],
                 [DATETIME[2], VALUE[2]]],
                [[DATETIME[3], GAP_VALUE]],
                [[DATETIME[4], VALUE[4]],
                 [DATETIME[5], VALUE[5]]]]

        result = _distribute_points_among_series_parts(5, data)

        self.assertEqual(result, [series_part(2, 0, data[0]), series_part(1, 0, data[1]), series_part(2, 0, data[2])])

    def test_num_points_to_distribute_between_big_and_small_parts_is_greater_than_num_bound_points_on_1(self):
        data = [[[DATETIME[0], VALUE[0]],
                 [DATETIME[1], VALUE[1]],
                 [DATETIME[2], VALUE[2]],
                 [DATETIME[3], VALUE[3]],
                 [DATETIME[4], VALUE[4]]],
                [[DATETIME[5], GAP_VALUE]],
                [[DATETIME[6], VALUE[6]],
                 [DATETIME[7], VALUE[7]],
                 [DATETIME[8], VALUE[8]],
                 [DATETIME[9], VALUE[9]]]]

        result = _distribute_points_among_series_parts(6, data)

        self.assertEqual(result, [series_part(2, 1, data[0]), series_part(1, 0, data[1]), series_part(2, 0, data[2])])

    def test_num_points_to_distribute_between_small_and_big_parts_is_greater_than_num_bound_points_on_1(self):
        data = [[[DATETIME[0], VALUE[0]],
                 [DATETIME[1], VALUE[1]],
                 [DATETIME[2], VALUE[2]],
                 [DATETIME[3], VALUE[3]]],
                [[DATETIME[4], GAP_VALUE]],
                [[DATETIME[5], VALUE[5]],
                 [DATETIME[6], VALUE[6]],
                 [DATETIME[7], VALUE[7]],
                 [DATETIME[8], VALUE[8]],
                 [DATETIME[9], VALUE[9]]]]

        result = _distribute_points_among_series_parts(6, data)

        self.assertEqual(result, [series_part(2, 0, data[0]), series_part(1, 0, data[1]), series_part(2, 1, data[2])])

    def test_num_points_to_distribute_between_almost_equal_parts_is_greater_than_num_bound_points_on_2(self):
        data = [[[DATETIME[0], VALUE[0]],
                 [DATETIME[1], VALUE[1]],
                 [DATETIME[2], VALUE[2]],
                 [DATETIME[3], VALUE[3]]],
                [[DATETIME[4], GAP_VALUE]],
                [[DATETIME[5], VALUE[5]],
                 [DATETIME[6], VALUE[6]],
                 [DATETIME[7], VALUE[7]],
                 [DATETIME[8], VALUE[8]],
                 [DATETIME[9], VALUE[9]]]]

        result = _distribute_points_among_series_parts(7, data)

        self.assertEqual(result, [series_part(2, 1, data[0]), series_part(1, 0, data[1]), series_part(2, 1, data[2])])


def series_part(boundary_points, allocated_points, series_part_data):
    return {"boundary_points": boundary_points,
            "allocated_points": allocated_points,
            "series_part": series_part_data}


def _distribute_points_among_series_parts(num_points, series):
    wrapped_series_parts = distribute_points_among_series_parts(num_points, series)
    return list(map(lambda w: series_part(w.boundary_points, w.allocated_points, w.original_series_part), wrapped_series_parts))


if __name__ == '__main__':
    unittest.main()
