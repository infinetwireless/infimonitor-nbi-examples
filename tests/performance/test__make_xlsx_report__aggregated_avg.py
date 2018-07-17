import unittest
from examples.performance.make_xlsx_report import *
from tests.performance.test__make_xlsx_report__format_vector import aggregated_value


class MakeXlsxReport_aggregated_avg_Tests(unittest.TestCase):

    def test_empty_int_parameter(self):
        value = aggregated_value()

        avg = aggregated_avg(value, IntParameter('int').inner_to_xlsx_value)

        self.assertTrue(math.isnan(avg))

    def test_int_parameter(self):
        value = aggregated_value(123)

        avg = aggregated_avg(value, IntParameter('int').inner_to_xlsx_value)

        self.assertEqual(123, avg)

    def test_empty_fixed_parameter(self):
        value = aggregated_value()

        avg = aggregated_avg(value, FixedPointParameter('fixed_point', 100).inner_to_xlsx_value)

        self.assertTrue(math.isnan(avg))

    def test_fixed_parameter(self):
        value = aggregated_value(12345)

        avg = aggregated_avg(value, FixedPointParameter('fixed_point', 100).inner_to_xlsx_value)

        self.assertEqual(123.45, avg)


if __name__ == '__main__':
    unittest.main()
