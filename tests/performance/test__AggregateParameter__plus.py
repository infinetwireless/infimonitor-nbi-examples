import unittest
from examples.performance.make_xlsx_report import *


class MakeExcelReport_format_values_Tests(unittest.TestCase):
    def test_plus_first_value(self):
        parameter = AggregatedParameter()

        parameter.plus(100)

        self.assertEqual(100, parameter.min)
        self.assertEqual(100, parameter.max)
        self.assertEqual(100, parameter.sum)
        self.assertEqual(1, parameter.count)
        self.assertEqual(type(parameter.sum), numpy.int64)

    def test_plus_few_values(self):
        parameter = AggregatedParameter()

        parameter.plus(100)
        parameter.plus(200)
        parameter.plus(40)

        self.assertEqual(40, parameter.min)
        self.assertEqual(200, parameter.max)
        self.assertEqual(340, parameter.sum)
        self.assertEqual(3, parameter.count)
        self.assertEqual(type(parameter.sum), numpy.int64)

if __name__ == '__main__':
    unittest.main()
