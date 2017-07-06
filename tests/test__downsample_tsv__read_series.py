import unittest
from examples.downsample_tsv import _read_series

HEADER = ['nmsObjectUuid', 'parameterName', 'timestamp', 'index', 'value']
DATETIME = list(map(lambda x: '2000-01-01T00:00:' + str(x).zfill(2) + 'Z', range(6)))
VALUE = list(map(lambda x: 100.0 + float(x), range(6)))
UUID1 = '11111111-1111-1111-1111-111111111111'
UUID2 = '22222222-2222-2222-2222-222222222222'
PARAMETER_NAME1 = 'txPowerDBm'
PARAMETER_NAME2 = 'currentLevel'


def _headers_processor(result):
    return lambda header: result.append(header)


def _series_processor(result):
    return lambda uuid, parameter, index, series: result.append([uuid, parameter, index, series])


class DownsampleTSV_ReadSeries_Tests(unittest.TestCase):
    def test_split_into_series_when_uuid_or_parameterName_changed(self):
        data = [HEADER,
                [UUID1, PARAMETER_NAME1, DATETIME[0], 0, VALUE[0]],
                [UUID1, PARAMETER_NAME1, DATETIME[1], 0, VALUE[1]],
                [UUID1, PARAMETER_NAME2, DATETIME[2], 0, VALUE[2]],
                [UUID1, PARAMETER_NAME2, DATETIME[3], 0, VALUE[3]],
                [UUID2, PARAMETER_NAME2, DATETIME[4], 0, VALUE[4]],
                [UUID2, PARAMETER_NAME2, DATETIME[5], 0, VALUE[5]]]

        headers, series = [], []
        _read_series(iter(data), _headers_processor(headers), _series_processor(series))

        self.assertEqual(len(headers), 1)
        self.assertEqual(headers[0], HEADER)
        self.assertEqual(len(series), 3)
        self.assertEqual(series[0], [UUID1, PARAMETER_NAME1, 0, [[DATETIME[0], VALUE[0]], [DATETIME[1], VALUE[1]]]])
        self.assertEqual(series[1], [UUID1, PARAMETER_NAME2, 0, [[DATETIME[2], VALUE[2]], [DATETIME[3], VALUE[3]]]])
        self.assertEqual(series[2], [UUID2, PARAMETER_NAME2, 0, [[DATETIME[4], VALUE[4]], [DATETIME[5], VALUE[5]]]])

    def test_split_into_series_when_indexes_interleaved(self):
        data = [HEADER,
                [UUID1, PARAMETER_NAME1, DATETIME[0], 0, VALUE[0]],
                [UUID1, PARAMETER_NAME1, DATETIME[1], 1, VALUE[1]],
                [UUID1, PARAMETER_NAME1, DATETIME[2], 0, VALUE[2]],
                [UUID1, PARAMETER_NAME1, DATETIME[3], 1, VALUE[3]]]

        headers, series = [], []
        _read_series(iter(data), _headers_processor(headers), _series_processor(series))

        self.assertEqual(len(headers), 1)
        self.assertEqual(headers[0], HEADER)
        self.assertEqual(len(series), 2)
        self.assertEqual(series[0], [UUID1, PARAMETER_NAME1, 0, [[DATETIME[0], VALUE[0]], [DATETIME[2], VALUE[2]]]])
        self.assertEqual(series[1], [UUID1, PARAMETER_NAME1, 1, [[DATETIME[1], VALUE[1]], [DATETIME[3], VALUE[3]]]])

    def test_split_into_series_when_indexes_sequential(self):
        data = [HEADER,
                [UUID1, PARAMETER_NAME1, DATETIME[0], 0, VALUE[0]],
                [UUID1, PARAMETER_NAME1, DATETIME[2], 0, VALUE[2]],
                [UUID1, PARAMETER_NAME1, DATETIME[1], 1, VALUE[1]],
                [UUID1, PARAMETER_NAME1, DATETIME[3], 1, VALUE[3]]]

        headers, series = [], []
        _read_series(iter(data), _headers_processor(headers), _series_processor(series))

        self.assertEqual(len(headers), 1)
        self.assertEqual(headers[0], HEADER)
        self.assertEqual(len(series), 2)
        self.assertEqual(series[0], [UUID1, PARAMETER_NAME1, 0, [[DATETIME[0], VALUE[0]], [DATETIME[2], VALUE[2]]]])
        self.assertEqual(series[1], [UUID1, PARAMETER_NAME1, 1, [[DATETIME[1], VALUE[1]], [DATETIME[3], VALUE[3]]]])


if __name__ == '__main__':
    unittest.main()
