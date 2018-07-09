import unittest
from examples.performance.make_xlsx_report import *


class MakeExcelReport_format_values_Tests(unittest.TestCase):
    def test_plus_two_aggregates_both_not_empty(self):
        first = AggregatedValue()
        first.aggregate(10)
        first.aggregate(20)
        first.aggregate(30)
        second = AggregatedValue()
        second.aggregate(100)
        second.aggregate(200)

        first.aggregate_other(second)

        self.assertEqual(10, first.min)
        self.assertEqual(200, first.max)
        self.assertEqual(360, first.sum)
        self.assertEqual(5, first.count)
        self.assertEqual(type(first.sum), numpy.int64)

    def test_plus_two_aggregates_first_is_empty(self):
        first = AggregatedValue()
        second = AggregatedValue()
        second.aggregate(100)
        second.aggregate(200)

        first.aggregate_other(second)

        self.assertEqual(100, first.min)
        self.assertEqual(200, first.max)
        self.assertEqual(300, first.sum)
        self.assertEqual(2, first.count)
        self.assertEqual(type(first.sum), numpy.int64)

    def test_plus_two_aggregates_second_is_empty(self):
        first = AggregatedValue()
        first.aggregate(10)
        first.aggregate(20)
        first.aggregate(30)
        second = AggregatedValue()

        first.aggregate_other(second)

        self.assertEqual(10, first.min)
        self.assertEqual(30, first.max)
        self.assertEqual(60, first.sum)
        self.assertEqual(3, first.count)
        self.assertEqual(type(first.sum), numpy.int64)

if __name__ == '__main__':
    unittest.main()
