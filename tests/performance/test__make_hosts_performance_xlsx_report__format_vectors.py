import unittest
from examples.performance.make_hosts_performance_xlsx_report import *
from tests.performance.test__make_xlsx_report__format_vector import aggregated_value

SOME_INT_PARAMETER = IntParameter('some_int')


class MakeHostsXlsxReport_format_vectors_Tests(unittest.TestCase):

    def test_empty_vectors(self):
        vectors = []

        result = format_vectors(vectors, SOME_INT_PARAMETER, aggregated_avg)

        self.assertEqual(NO_DATA, result)

    def test_single_valued_vectors(self):
        vectors = [vector(SOME_INT_PARAMETER, aggregated_value(100))]

        result = format_vectors(vectors, SOME_INT_PARAMETER, aggregated_avg)

        self.assertEqual(100, result)

    def test_two_valued_vectors(self):
        vectors = [vector(SOME_INT_PARAMETER, aggregated_value(100)),
                   vector(SOME_INT_PARAMETER, aggregated_value(200))]

        result = format_vectors(vectors, SOME_INT_PARAMETER, aggregated_avg)

        self.assertEqual('100.0, 200.0', result)


def vector(parameter, *aggregated_values):
    result = Vector()
    result.parameters[parameter.name] = list(aggregated_values)
    return result


if __name__ == '__main__':
    unittest.main()
