import argparse
import csv
from datetime import datetime as dt
import math
import numpy
import os
import sys
import traceback
import xlsxwriter

NO_DATA = 'N/A'


class StringParameter:
    def __init__(self, name):
        self.name = name

    def tsv_to_inner_value(self, string):
        return string

    def inner_to_xlsx_value(self, value):
        return value


class IntParameter:
    def __init__(self, name):
        self.name = name

    def tsv_to_inner_value(self, string):
        return int(string)

    def inner_to_xlsx_value(self, value):
        return value


class FixedPointParameter:
    def __init__(self, name, scaling_factor):
        self.name = name
        self.scaling_factor = scaling_factor

    def tsv_to_inner_value(self, string):
        return int(float(string) * self.scaling_factor)

    def inner_to_xlsx_value(self, value):
        return value / self.scaling_factor


class AggregatedValue:
    def __init__(self):
        self.min = None
        self.max = None
        self.sum = numpy.int64(0)
        self.count = 0

    def __eq__(self, other):
        if not isinstance(other, AggregatedValue):
            return False
        return self.min == other.min and \
               self.max == other.max and \
               self.sum == other.sum and \
               self.count == other.count

    def __repr__(self):
        return "{{min={0}, max={1}, sum={2}, count={3}}}".format(self.min, self.max, self.sum, self.count)

    def aggregate(self, value):
        if self.min is None:
            self.min = value
        if self.max is None:
            self.max = value
        if value < self.min:
            self.min = value
        elif value > self.max:
            self.max = value
        self.sum += numpy.int64(value)
        self.count += 1


class Column:
    def __init__(self, display_name, formatter=None, width=None, sub_columns=[]):
        self.display_name = display_name
        self.format_values = formatter
        self.width = width
        self.sub_columns = sub_columns


class ColumnPrototype:
    def __init__(self, column_display_name, parameter):
        self.column_display_name = column_display_name
        self.parameter = parameter


R5000_AGGREGATED_COLUMNS_PROTOTYPES = [
    ColumnPrototype('Rx Level dB', IntParameter('currentLevel')),
    ColumnPrototype('Tx retries %', IntParameter('retries')),
    ColumnPrototype('Tx bitrate Mbps', IntParameter('bitrate'))]

XG_AGGREGATED_COLUMNS_PROTOTYPES = [
    ColumnPrototype('CINR dBm', IntParameter('xgCINR')),
    ColumnPrototype('absolute RSSI dBm', IntParameter('xgABSRSSI')),
    ColumnPrototype('total Tx capacity Mbps', FixedPointParameter('xgTotalCapacityTx', 100))]


def columns_tree(aggregated_columns_prototypes):
    def create_formatter(link_to_vector, parameter, aggregated_value_transform):
        return lambda link: format_vector(link_to_vector(link), parameter, aggregated_value_transform)

    def link_to_vector_a(link):
        return link.vector_a

    def link_to_vector_b(link):
        return link.vector_b

    columns = [Column('Link', sub_columns=[
        Column('Host A', lambda link: host_label(link.host_a), 12),
        Column('Host B', lambda link: host_label(link.host_b), 12)])]
    for prototype in aggregated_columns_prototypes:
        column_display_name, parameter = prototype.column_display_name, prototype.parameter
        width = 9
        columns.append(
            Column('Host A {0}'.format(column_display_name), sub_columns=[
                Column('Avg', create_formatter(link_to_vector_a, parameter, aggregated_avg), width),
                Column('Min', create_formatter(link_to_vector_a, parameter, aggregated_min), width),
                Column('Max', create_formatter(link_to_vector_a, parameter, aggregated_max), width)]))
        columns.append(
            Column('Host B {0}'.format(column_display_name), sub_columns=[
                Column('Avg', create_formatter(link_to_vector_b, parameter, aggregated_avg), width),
                Column('Min', create_formatter(link_to_vector_b, parameter, aggregated_min), width),
                Column('Max', create_formatter(link_to_vector_b, parameter, aggregated_max), width)]))
    return Column(None, sub_columns=columns)


def aggregated_avg(aggregated_value, inner_to_xlsx_value):
    if not aggregated_value.count:
        return float('NaN')
    return int(inner_to_xlsx_value(aggregated_value.sum) * 100 / aggregated_value.count) / 100


def aggregated_min(aggregated_value, inner_to_xlsx_value):
    return inner_to_xlsx_value(aggregated_value.min)


def aggregated_max(aggregated_value, inner_to_xlsx_value):
    return inner_to_xlsx_value(aggregated_value.max)


def format_vector(vector, parameter, aggregated_value_transform):
    if vector is None:
        return NO_DATA
    aggregated_values = vector.parameters.get(parameter.name)
    if not aggregated_values:
        return NO_DATA
    values = map(lambda value: aggregated_value_transform(value, parameter.inner_to_xlsx_value), aggregated_values)
    values = filter(lambda value: not math.isnan(value), values)
    values = list(values)
    if len(values) < 1:
        return NO_DATA
    return max(values)


class Host:
    def __init__(self, exists, activated):
        self.exists = exists
        self.activated = activated
        self.parameters = {}

    def append_parameter_value(self, parameter_name, parameter_value):
        if parameter_name not in self.parameters:
            self.parameters[parameter_name] = []  # some parameters can be multivalued, like IP address
        self.parameters[parameter_name].append(parameter_value)

    def label(self):
        if 'hostLabel' not in self.parameters:
            return NO_DATA
        values = self.parameters['hostLabel']
        if len(values) < 1:
            return NO_DATA
        return values[0]

    def ips(host):
        if not host:
            return NO_DATA
        if 'ipAdEntAddr' not in host.parameters:
            return NO_DATA
        values = host.parameters['ipAdEntAddr']
        values = filter(lambda value: value != '127.0.0.1', values)
        values = sorted(values)
        return ", ".join(values)

    def is_xg(self):
        return self.parameters['productFamily'][0] == 'XG'


def host_label(host):
    return host.label() if host else NO_DATA


class Link:
    def __init__(self, host_a_uuid, host_b_uuid, vector_a_uuid, vector_b_uuid):
        self.host_a_uuid = host_a_uuid
        self.host_b_uuid = host_b_uuid
        self.vector_a_uuid = vector_a_uuid
        self.vector_b_uuid = vector_b_uuid
        self.parameters = {}
        self.host_a = None
        self.host_b = None
        self.vector_a = None
        self.vector_b = None

    def label(self):
        return host_label(self.host_a) + '→' + host_label(self.host_b)

    def is_xg(self):
        return self.host_a.is_xg()  # always same as self.host_b.is_xg()


class Vector:
    def __init__(self):
        self.parameters = {}

    def aggregate(self, parameter, index, value):
        if parameter.name not in self.parameters:
            self.parameters[parameter.name] = []
        parameter_values = self.parameters[parameter.name]
        if index >= len(parameter_values):
            parameter_values.extend([AggregatedValue() for _ in range(len(parameter_values), index + 1)])
        parameter_value = parameter_values[index]
        parameter_value.aggregate(value)


def read_hosts(data_dir):
    host_uuid_to_host = {}
    with open(data_dir + '/hosts.tsv', 'rt') as file:
        reader = csv.reader(file, dialect='excel-tab')
        next(reader, None)  # skip headers
        for host_uuid, exists, activated in reader:
            host = Host(exists.lower() == 'true', activated.lower() == 'true')
            host_uuid_to_host[host_uuid] = host

    iface_uuid_to_host_uuid = {}
    with open(data_dir + '/hosts_interfaces.tsv', 'rt') as file:
        reader = csv.reader(file, dialect='excel-tab')
        next(reader, None)  # skip headers
        for host_uuid, iface_uuid, exists, activated in reader:
            iface_uuid_to_host_uuid[iface_uuid] = host_uuid

    with open(data_dir + '/hosts_parameters.tsv', 'rt') as file:
        reader = csv.reader(file, dialect='excel-tab')
        next(reader, None)  # skip headers
        for host_uuid, parameter_name, timestamp, index, value in reader:
            if host_uuid not in host_uuid_to_host:
                continue  # hosts and its parameters are loaded separately so they may be a bit inconsistent
            host = host_uuid_to_host[host_uuid]
            host.append_parameter_value(parameter_name, value)

    with open(data_dir + '/interfaces_parameters.tsv', 'rt') as file:
        reader = csv.reader(file, dialect='excel-tab')
        next(reader, None)  # skip headers
        for iface_uuid, parameter_name, timestamp, index, value in reader:
            if iface_uuid not in iface_uuid_to_host_uuid:
                # hosts_interfaces and interfaces parameters are loaded separately. so they may be a bit inconsistent
                continue
            host_uuid = iface_uuid_to_host_uuid[iface_uuid]
            host = host_uuid_to_host[host_uuid]
            host.append_parameter_value(parameter_name, value)

    return host_uuid_to_host


def read_aggregated_vectors(data_dir, name_to_parameter):
    with open(data_dir + '/vectors_history.tsv', 'rt') as file:
        reader = csv.reader(file, dialect='excel-tab')
        next(reader, None)  # skip headers
        uuid_to_vector = {}
        for vector_uuid, parameter_name, _, index, value in reader:
            index = int(index)
            if vector_uuid not in uuid_to_vector:
                uuid_to_vector[vector_uuid] = Vector()
            vector = uuid_to_vector[vector_uuid]
            if value != 'null':
                if parameter_name in name_to_parameter:
                    parameter = name_to_parameter[parameter_name]
                    value = parameter.tsv_to_inner_value(value)
                    vector.aggregate(parameter, index, value)
        return uuid_to_vector


def read_links(data_dir):
    with open(data_dir + '/vectors_parameters.tsv', 'rt') as file:
        reader = csv.reader(file, dialect='excel-tab')
        next(reader, None)  # skip headers
        uuid_to_vector_type = {}
        for vector_uuid, parameter_name, _, _, value in reader:
            if parameter_name == 'vectorType':
                uuid_to_vector_type[vector_uuid] = value
    with open(data_dir + '/links.tsv', 'rt') as file:
        reader = csv.reader(file, dialect='excel-tab')
        next(reader, None)  # skip headers
        links = []
        for _, _, _, host_a_uuid, host_b_uuid, _, _, vector_a_uuid, vector_b_uuid in reader:
            # vectors_parameters.tsv used to filter out links with types other than radio
            # operator or cause one of the vector may be absent
            if vector_a_uuid in uuid_to_vector_type or vector_b_uuid in uuid_to_vector_type:
                links.append(Link(host_a_uuid, host_b_uuid, vector_a_uuid, vector_b_uuid))
        return links


def enrich_links(links, uuid_to_host, uuid_to_aggregated_vector):
    for link in links:
        link.host_a = uuid_to_host.get(link.host_a_uuid)
        link.host_b = uuid_to_host.get(link.host_b_uuid)
        link.vector_a = uuid_to_aggregated_vector.get(link.vector_a_uuid)
        link.vector_b = uuid_to_aggregated_vector.get(link.vector_a_uuid)


def make_header(worksheet, columns_tree, header_format, height):
    worksheet.freeze_panes(height, 0)

    def traverse(columns_tree, level, x, column_processor):
        is_leaf = len(columns_tree.sub_columns) == 0
        if is_leaf:
            span = 1
        else:
            span = 0
            for child in columns_tree.sub_columns:
                span += traverse(child, level + 1, x + span, column_processor)
        column_processor(columns_tree, level, x, span, is_leaf)
        return span

    leaf_columns = []

    def column_processor(column, level, x, span, is_leaf):
        if level == 0:
            return
        y = level - 1
        text = column.display_name if column.display_name else ''
        if is_leaf:
            leaf_columns.append(column)
            if y < height - 1:
                worksheet.merge_range(y, x, height - 1, x, text, header_format)
            else:
                worksheet.write(y, x, text, header_format)
        else:
            if span > 1:
                worksheet.merge_range(y, x, y, x + span - 1, text, header_format)
            else:
                worksheet.write(y, x, text, header_format)
        if column.width:
            worksheet.set_column(x, x, column.width)

    traverse(columns_tree, 0, 0, column_processor)
    return leaf_columns


class LinksView:
    def __init__(self, name, aggregated_columns_prototypes, filter):
        self.name = name
        self.aggregated_columns_prototypes = aggregated_columns_prototypes
        self.filter = filter


def make_report(data_dir, report_file):
    views = [LinksView("R5000 radio", R5000_AGGREGATED_COLUMNS_PROTOTYPES, lambda link: not link.is_xg()),
             LinksView("XG radio", XG_AGGREGATED_COLUMNS_PROTOTYPES, lambda link: link.is_xg())]
    name_to_parameter = {prototype.parameter.name: prototype.parameter
                         for view in views
                         for prototype in view.aggregated_columns_prototypes}

    with xlsxwriter.Workbook(report_file) as workbook:
        header_format = workbook.add_format()
        header_format.set_bold()
        header_format.set_align('center')
        header_format.set_align('vcenter')
        header_format.set_border()

        uuid_to_host = read_hosts(data_dir)
        uuid_to_aggregated_vector = read_aggregated_vectors(data_dir, name_to_parameter)
        links = read_links(data_dir)
        enrich_links(links, uuid_to_host, uuid_to_aggregated_vector)

        for view in views:
            worksheet = workbook.add_worksheet(view.name)
            view_links = filter(view.filter, links)
            view_links = list(view_links)
            view_links = sorted(view_links, key=lambda link: link.label())
            view_columns_tree = columns_tree(view.aggregated_columns_prototypes)
            leaf_columns = make_header(worksheet, view_columns_tree, header_format, 2)
            for i, link in enumerate(view_links, 2):
                for j, column in enumerate(leaf_columns):
                    worksheet.write(i, j, column.format_values(link))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir',
                        help='directory with report data files: hosts.tsv, hosts_interfaces.tsv,'
                             ' links.tsv, hosts_parameters.tsv, interfaces_parameters.tsv, vectors_parameters.tsv,'
                             ' vectors_history.tsv',
                        required=True)
    parser.add_argument('--report-file',
                        help='path to the xlsx report file',
                        default='performance.xlsx')
    args = parser.parse_args()

    started_at = dt.now()
    try:
        make_report(args.data_dir, args.report_file)
        sys.stderr.write("Done at " + str(dt.now() - started_at) + "\n")
        sys.stderr.write("Report available at " + os.path.abspath(args.report_file) + "\n")
    except Exception:
        sys.stderr.write("Failed:\n")
        traceback.print_exc()
        if os.path.exists(args.report_file):
            os.remove(args.report_file)
        exit(1)
