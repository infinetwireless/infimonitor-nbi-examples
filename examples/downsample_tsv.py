import argparse
import csv
import re
from datetime import datetime as dt

GAP_VALUE = 'null'
parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--downsample-to', type=int, default='10')
# args = parser.parse_args()
args = parser.parse_args(['--input', '../out/vectors.tsv', '--output', '../out/downsampled_vectors.tsv'])


def parse_datetime(datetime_str):
    def reassemble(matches):
        group2 = matches.group(2)
        return matches.group(1) + (group2 if group2 else '.0') + matches.group(3) + matches.group(4)

    normalized_z_time_zone = datetime_str.replace('Z', '+00:00')
    normalized_microseconds = re.sub('([^.]+)(\.\d+)?([+-]\d\d):(\d\d)', reassemble, normalized_z_time_zone)
    return dt.strptime(normalized_microseconds, "%Y-%m-%dT%H:%M:%S.%f%z")


def read_series(file_name, headers_processor, series_processor):
    with open(file_name, 'rt') as csv_file:
        reader = csv.reader(csv_file, dialect='excel-tab')
        series_processor(reader, headers_processor, series_processor)


def _read_series(reader, headers_processor, series_processor):
    headers_processor(next(reader))
    index_to_series = {}
    prev_nms_object_uuid, prev_parameter_name = None, None
    for nms_object_uuid, parameter_name, datetime, index, value in reader:
        if prev_nms_object_uuid == nms_object_uuid and prev_parameter_name == parameter_name:
            if index not in index_to_series:
                index_to_series[index] = []
            index_to_series[index].append([datetime, value])
        else:  # series ended
            for series_index, series in index_to_series.items():
                series_processor(prev_nms_object_uuid, prev_parameter_name, series_index, series)
            index_to_series = {index: [[datetime, value]]}  # new series
            prev_nms_object_uuid, prev_parameter_name = nms_object_uuid, parameter_name
    for series_index, series in index_to_series.items():
        series_processor(prev_nms_object_uuid, prev_parameter_name, series_index, series)


def split_by_gaps(is_gap, series):
    parts = []
    last_part = []
    for datetime_value in series:
        if is_gap(datetime_value):
            if last_part:
                parts.append(last_part)
                parts.append([datetime_value])
                last_part = []
            elif not parts:
                parts.append([datetime_value])
                last_part = []
        else:
            last_part.append(datetime_value)
    if last_part:
        parts.append(last_part)
    return parts


class TimestampedValue(list):
    def __init__(self, datetime_value):
        list.__init__(self)
        self.append(parse_datetime(datetime_value[0]).timestamp())
        self.append(None if datetime_value[1] == GAP_VALUE else float(datetime_value[1]))
        self.original = datetime_value

    def is_gap(self):
        return not self[1]


class SeriesPart:
    def __init__(self, series_part):
        self.series_part = series_part
        self.boundary_points = 1 if len(series_part) == 1 else 2
        self.allocated_points = 0

    def duration(self):
        return self.series_part[-1][0] - self.series_part[0][0]

    def __lt__(self, other):
        return self.allocated_points / self.duration() < other.allocated_points / other.duration()

    def downsample(self):
        num_target_points = self.boundary_points + self.allocated_points
        if num_target_points < 3:
            return self.series_part
        else:
            return lttb.downsample(self.series_part, num_target_points)


if __name__ == '__main__':
    with open(args.output, 'wt') as csv_file:
        writer = csv.writer(csv_file, dialect='excel-tab')
        read_series(args.input, writer.writerow, process_series)

# min_points = len(series_continuous_parts) * 3 - 1  # 3 ponits in min part - start point, end point, gap
#         max_points = sum(map(series_continuous_parts, lambda s: len(s) + 1)) - 1
#         downsampled = lttb.lttb.downsample(np.array(series), args.downsample_to) \
#             if len(series) > args.downsample_to \
#             else series
#         value = None if value == 'null' else
#         if not value:
#             continue
#
#
#     for datetime in downsampled:
#         writer.writerow([nms_object_uuid, parameter_name, datetime[0], index, datetime[1]])
#
#
