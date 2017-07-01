import csv
import argparse
import re
from datetime import datetime as dt
import numpy as np
import lttb

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

    normalized_time_zone = datetime_str.replace('Z', '+00:00')
    normalized_subseconds = re.sub('([^.]+)(\.\d+)?([+-]\d\d):(\d\d)', reassemble, normalized_time_zone)
    return dt.strptime(normalized_subseconds, "%Y-%m-%dT%H:%M:%S.%f%z")


def read_series(file_name, process_headers, process_series):
    with open(file_name, 'rt') as csv_file:
        reader = csv.reader(csv_file, dialect='excel-tab')
        index_to_series = {}
        prev_nms_object_uuid, prev_parameter_name = None, None
        process_headers(next(reader))
        for nms_object_uuid, parameter_name, datetime, index, value in reader:
            if prev_nms_object_uuid == nms_object_uuid and prev_parameter_name == parameter_name:
                if index not in index_to_series:
                    index_to_series[index] = []
                index_to_series[index].append([datetime, value])
            else:  # series ended
                for series_index, series in index_to_series.items():
                    process_series(nms_object_uuid, parameter_name, series_index, series)
                index_to_series = {}  # clear old series
                prev_nms_object_uuid, prev_parameter_name = nms_object_uuid, parameter_name


with open(args.output, 'wt') as csv_file:
    writer = csv.writer(csv_file, dialect='excel-tab')


    def process_series(nms_object_uuid, parameter_name, index, series):
        series_continuous_parts = []
        last_part = []
        for datetime_str, value_str in series:
            if value_str == 'null':
                if last_part:
                    series_continuous_parts.append(last_part)
                    last_part = []
            else:
                last_part.append(
                    [parse_datetime(datetime_str).timestamp(), float(value_str), datetime_str, value_str])
        if last_part:
            series_continuous_parts.append(last_part)

#         min_points = len(series_continuous_parts) * 3 - 1  # 3 ponits in min part - start point, end point, gap
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
# read_series(args.input, writer.writerow, process_series)
