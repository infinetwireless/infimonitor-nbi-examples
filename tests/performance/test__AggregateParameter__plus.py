import unittest
from examples.performance.make_xlsx_report import *


class MakeXlsxReport_format_values_Tests(unittest.TestCase):
    def test_plus_first_value(self):
        parameter = AggregatedValue()

        parameter.aggregate(100)

        self.assertEqual(100, parameter.min)
        self.assertEqual(100, parameter.max)
        self.assertEqual(100, parameter.sum)
        self.assertEqual(1, parameter.count)
        self.assertEqual(type(parameter.min), int)
        self.assertEqual(type(parameter.max), int)
        self.assertEqual(type(parameter.sum), numpy.int64)
        self.assertEqual(type(parameter.count), int)

    def test_plus_few_values(self):
        parameter = AggregatedValue()

        parameter.aggregate(100)
        parameter.aggregate(200)
        parameter.aggregate(40)

        self.assertEqual(40, parameter.min)
        self.assertEqual(200, parameter.max)
        self.assertEqual(340, parameter.sum)
        self.assertEqual(3, parameter.count)
        self.assertEqual(type(parameter.min), int)
        self.assertEqual(type(parameter.max), int)
        self.assertEqual(type(parameter.sum), numpy.int64)
        self.assertEqual(type(parameter.count), int)

if __name__ == '__main__':
    unittest.main()
