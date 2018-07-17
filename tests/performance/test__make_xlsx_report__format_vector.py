import unittest
from examples.performance.make_xlsx_report import *

SOME_PARAMETER = IntParameter('some_int')


class MakeXlsxReport_format_vector_Tests(unittest.TestCase):

    def test_absent_vector(self):
        vector = None

        result = format_vector(vector, SOME_PARAMETER, aggregated_avg)

        self.assertEqual(NO_DATA, result)

    def test_absent_vector_parameter(self):
        vector = Vector()

        result = format_vector(vector, SOME_PARAMETER, aggregated_avg)

        self.assertEqual(NO_DATA, result)

    def test_single_valued_vector_parameter(self):
        vector = Vector()
        vector.parameters[SOME_PARAMETER.name] = [aggregated_value(100)]

        result = format_vector(vector, SOME_PARAMETER, aggregated_avg)

        self.assertEqual(100, result)

    def test_single_valued_NaN_vector_parameter(self):
        vector = Vector()
        vector.parameters[SOME_PARAMETER.name] = [aggregated_value()]

        result = format_vector(vector, SOME_PARAMETER, aggregated_avg)

        self.assertEqual(NO_DATA, result)

    def test_max_of_two_valued_vector_parameter(self):
        vector = Vector()
        vector.parameters[SOME_PARAMETER.name] = [aggregated_value(100), aggregated_value(200)]

        result = format_vector(vector, SOME_PARAMETER, aggregated_avg)

        self.assertEqual(200, result)

    def test_max_of_two_valued_NaN_vector_parameter(self):
        vector = Vector()
        vector.parameters[SOME_PARAMETER.name] = [aggregated_value(), aggregated_value(200)]

        result = format_vector(vector, SOME_PARAMETER, aggregated_avg)

        self.assertEqual(200, result)


def aggregated_value(*values):
    result = AggregatedValue()
    for value in values:
        result.aggregate(value)
    return result


if __name__ == '__main__':
    unittest.main()
