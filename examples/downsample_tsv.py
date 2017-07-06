import sys
import argparse
import csv
import re
import numpy as np
from datetime import datetime as dt
from heapq import heappush, heappop, heapify
from examples.lttb import downsample as lttb_downsample

GAP_VALUE = 'null'


def parse_datetime(datetime_str):
    def reassemble(matches):
        group2 = matches.group(2)
        return matches.group(1) + (group2 if group2 else '.0') + matches.group(3) + matches.group(4)

    normalized_z_time_zone = datetime_str.replace('Z', '+00:00')
    normalized_microseconds = re.sub('([^.]+)(\.\d+)?([+-]\d\d):(\d\d)', reassemble, normalized_z_time_zone)
    return dt.strptime(normalized_microseconds, "%Y-%m-%dT%H:%M:%S.%f%z")


def read_series(reader, headers_processor, series_processor):
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


class WrappedSeriesPart:
    def __init__(self, series_part):
        self.original_series_part = series_part
        self.np_series_part = np.zeros((len(series_part), 3))
        for i, datetime_value in enumerate(series_part):
            self.np_series_part[i][0] = parse_datetime(datetime_value[0]).timestamp()
            self.np_series_part[i][1] = None if datetime_value[1] == GAP_VALUE else float(datetime_value[1])
            self.np_series_part[i][2] = i
        self.boundary_points = min(len(series_part), 2)
        self.allocated_points = 0

    def duration(self):
        return self.np_series_part[-1][0] - self.np_series_part[0][0] if self.np_series_part.shape[0] > 0 else 0

    def density(self):
        return (1 + self.allocated_points) / self.duration()

    def __lt__(self, other):
        return self.density() < other.density()

    def downsample(self):
        num_source_points = len(self.original_series_part)
        num_target_points = self.boundary_points + self.allocated_points

        def _downsample():
            if num_source_points <= num_target_points:
                return self.np_series_part
            if num_target_points >= 3:
                return lttb_downsample(self.np_series_part, num_target_points)
            if num_target_points == 2:
                return np.array([self.np_series_part[0], self.np_series_part[-1]])
            raise Exception("Can't downsample number of points from %d to %d" % (num_source_points, num_target_points))

        def restore(timestamp_value_index):
            return self.original_series_part[int(round(timestamp_value_index[2]))]

        return list(map(restore, _downsample()))


def distribute_points_among_series_parts(num_points, series_parts):
    wrapped_series_parts = list(map(lambda s: WrappedSeriesPart(s), series_parts))
    num_boundary_points = sum(map(lambda s: s.boundary_points, wrapped_series_parts))
    series_parts_duration = sum(map(lambda s: s.duration(), wrapped_series_parts))
    num_left_points = num_points - num_boundary_points
    if num_left_points > 0 and series_parts_duration > 0:
        points_by_duration = num_left_points / series_parts_duration
        not_zero_duration_series_parts = list(filter(lambda s: s.boundary_points == 2, wrapped_series_parts))
        for series_part in not_zero_duration_series_parts:
            points = int(series_part.duration() * points_by_duration)
            num_left_points -= points
            series_part.allocated_points += points
        if num_left_points > 0:
            heap = list(not_zero_duration_series_parts)
            heapify(heap)
            for x in range(num_left_points):
                series_part = heappop(heap)
                series_part.allocated_points += 1
                heappush(heap, series_part)
    return wrapped_series_parts


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--downsample-to', type=int, default='100', help='desired number of points per series')
    parser.add_argument('--input', help='input tsv file otherwise stdin will be used')
    parser.add_argument('--output', help='output tsv file otherwise stdout will be used')
    args = parser.parse_args()

    with open(args.input, 'rt') if args.input else sys.stdin as input_file, \
            open(args.output, 'w') if args.output else sys.stdout as output_file:
        reader = csv.reader(input_file, dialect='excel-tab')
        writer = csv.writer(output_file, dialect='excel-tab')


        def series_processor(nms_object_uuid, parameter_name, index, series):
            series_parts = split_by_gaps(lambda datetime_value: datetime_value[1] == GAP_VALUE, series)
            wrapped_series_parts = distribute_points_among_series_parts(args.downsample_to, series_parts)
            for wrapped_series_part in wrapped_series_parts:
                downsampled_series_part = wrapped_series_part.downsample()
                for datetime_value in downsampled_series_part:
                    writer.writerow([nms_object_uuid, parameter_name, datetime_value[0], index, datetime_value[1]])


        read_series(reader, writer.writerow, series_processor)
