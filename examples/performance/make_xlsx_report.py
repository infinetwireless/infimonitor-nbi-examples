import argparse
from collections import OrderedDict
import csv
from datetime import datetime as dt
import numpy
import os
import sys
import traceback
import xlsxwriter

AGGREGATED_VECTOR_PARAMETERS = OrderedDict([
    ('currentLevel', 'Level dB'),
    ('retries', 'Retries %'),
    ('bitrate', 'Bitrate Mbps')])
NO_DATA = 'N/A  '


class Host:
    def __init__(self, exists, activated):
        self.exists = exists
        self.activated = activated
        self.parameters = {}
        self.interfaces = {}

    def add_parameter_value(self, parameter_name, parameter_value):
        if parameter_name not in self.parameters:
            self.parameters[parameter_name] = []  # some host parameters can be multivalued
        self.parameters[parameter_name].append(parameter_value)

    def plus_aggregated_parameter(self, parameter_name, aggregated_parameter):
        if parameter_name not in self.parameters:
            self.parameters[parameter_name] = AggregatedParameter()
        self.parameters[parameter_name].plus_aggregated(aggregated_parameter)


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
            host.add_parameter_value(parameter_name, value)

    with open(data_dir + '/interfaces_parameters.tsv', 'rt') as file:
        reader = csv.reader(file, dialect='excel-tab')
        next(reader, None)  # skip headers
        for iface_uuid, parameter_name, timestamp, index, value in reader:
            if iface_uuid not in iface_uuid_to_host_uuid:
                continue  # hosts_interfaces and interfaces parameters are loaded separately so they may be a bit inconsistent
            host_uuid = iface_uuid_to_host_uuid[iface_uuid]
            host = host_uuid_to_host[host_uuid]
            host.add_parameter_value(parameter_name, value)

    return host_uuid_to_host


class AggregatedParameter:
    def __init__(self):
        self.min = None
        self.max = None
        self.sum = numpy.int64(0)
        self.count = 0

    def __eq__(self, other):
        if not isinstance(other, AggregatedParameter):
            return False
        return self.min == other.min and \
               self.max == other.max and \
               self.sum == other.sum and \
               self.count == other.count

    def __repr__(self):
        return "{{min={0}, max={1}, sum={2}, count={3}}}".format(self.min, self.max, self.sum, self.count)

    def plus(self, value):
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

    def plus_aggregated(self, other):
        if self.count == 0:
            self.min = other.min
            self.max = other.max
            self.sum = other.sum
            self.count = other.count
        elif other.count != 0:
            self.min = min(self.min, other.min)
            self.max = max(self.max, other.max)
            self.sum = self.sum + other.sum
            self.count = self.count + other.count


class AggregatedVector:
    def __init__(self):
        self.parameters = {}

    def plus_parameter_value(self, parameter_name, value):
        if parameter_name not in self.parameters:
            self.parameters[parameter_name] = AggregatedParameter()
        parameter = self.parameters[parameter_name]
        parameter.plus(value)


def read_aggregated_vectors(data_dir):
    with open(data_dir + '/vectors_history.tsv', 'rt') as file:
        reader = csv.reader(file, dialect='excel-tab')
        next(reader, None)  # skip headers
        uuid_to_vector = {}
        for vector_uuid, parameterName, _, _, value in reader:
            if vector_uuid not in uuid_to_vector:
                uuid_to_vector[vector_uuid] = AggregatedVector()
            vector = uuid_to_vector[vector_uuid]
            if value != 'null':
                vector.plus_parameter_value(parameterName, value)
        return uuid_to_vector


class Link:
    def __init__(self, host_a_uuid, host_b_uuid, vector_a_uuid, vector_b_uuid):
        self.parameters = {}
        self.host_a_uuid = host_a_uuid
        self.host_b_uuid = host_b_uuid
        self.vector_a_uuid = vector_a_uuid
        self.vector_b_uuid = vector_b_uuid


def read_links(data_dir):
    with open(data_dir + '/links.tsv', 'rt') as file:
        reader = csv.reader(file, dialect='excel-tab')
        next(reader, None)  # skip headers
        links = []
        for _, _, _, host_a_uuid, host_b_uuid, _, _, vector_a_uuid, vector_b_uuid in reader:
            links.append(Link(host_a_uuid, host_b_uuid, vector_a_uuid, vector_b_uuid))
        return links


def tx_aggregated_parameter_name(parameter_name):
    return 'TX_{0}'.format(parameter_name.upper())


def rx_aggregated_parameter_name(parameter_name):
    return 'RX_{0}'.format(parameter_name.upper())


def enrich_hosts_parameters(host_uuid_to_host, links, uuid_to_aggregated_vector, parameters_names):
    for link in links:
        if link.host_a_uuid not in host_uuid_to_host or \
                link.host_b_uuid not in host_uuid_to_host or \
                link.vector_a_uuid not in uuid_to_aggregated_vector or \
                link.vector_a_uuid not in uuid_to_aggregated_vector:
            continue  # hosts, links and vectors are loaded separately so they may be a bit inconsistent
        host_a = host_uuid_to_host[link.host_a_uuid]
        host_b = host_uuid_to_host[link.host_b_uuid]
        aggregated_vector_a = uuid_to_aggregated_vector[link.vector_a_uuid]
        aggregated_vector_b = uuid_to_aggregated_vector[link.vector_b_uuid]
        for parameter_name in parameters_names:
            tx_parameter_name = tx_aggregated_parameter_name(parameter_name)
            rx_parameter_name = rx_aggregated_parameter_name(parameter_name)

            aggregated_parameter_a = aggregated_vector_a.parameters.get(parameter_name, AggregatedParameter())
            aggregated_parameter_b = aggregated_vector_b.parameters.get(parameter_name, AggregatedParameter())

            host_a.plus_aggregated_parameter(tx_parameter_name, aggregated_parameter_a)
            host_a.plus_aggregated_parameter(rx_parameter_name, aggregated_parameter_b)
            host_b.plus_aggregated_parameter(tx_parameter_name, aggregated_parameter_b)
            host_b.plus_aggregated_parameter(rx_parameter_name, aggregated_parameter_a)


class Column:
    def __init__(self, header, parameter_name=None, width=None, sub_columns=[]):
        self.header = header
        self.parameter_name = parameter_name
        self.width = width
        self.sub_columns = sub_columns


def columns_tree():
    columns = [
        Column('Host name', 'hostLabel', 15),
        Column('IP address', 'ipAdEntAddr', 25)]

    for parameter_name, parameter_label in AGGREGATED_VECTOR_PARAMETERS.items():
        width = 8
        columns.append(
            Column('Rx {0}'.format(parameter_label), sub_columns=[
                Column('Avg', rx_aggregated_parameter_name(parameter_name + '_AVG'), width),
                Column('Min', rx_aggregated_parameter_name(parameter_name + '_MIN'), width),
                Column('Max', rx_aggregated_parameter_name(parameter_name + '_MAX'), width)]))
        columns.append(
            Column('Tx {0}'.format(parameter_label), sub_columns=[
                Column('Avg', tx_aggregated_parameter_name(parameter_name + '_AVG'), width),
                Column('Min', tx_aggregated_parameter_name(parameter_name + '_MIN'), width),
                Column('Max', tx_aggregated_parameter_name(parameter_name + '_MAX'), width)]))
    return Column(None, None, sub_columns=columns)


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
        text = column.header if column.header else ''
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


def format_values(host, parameter_name):
    def if_suffix_apply(suffix, eval):
        if parameter_name.endswith(suffix):
            aggregated_parameter_name = parameter_name[:-len(suffix)]
            if aggregated_parameter_name not in host.parameters:
                return '-'
            aggregated_parameter = host.parameters[aggregated_parameter_name]
            return eval(aggregated_parameter)
        return None

    def avg(aggregated_parameter):
        if aggregated_parameter.count == 0:
            return NO_DATA
        return '{0:.1f}'.format(aggregated_parameter.sum / aggregated_parameter.count)

    result = if_suffix_apply('_AVG', avg) or \
             if_suffix_apply('_MIN', lambda aggregated_parameter: aggregated_parameter.min) or \
             if_suffix_apply('_MAX', lambda aggregated_parameter: aggregated_parameter.max)
    if result:
        return result
    if parameter_name not in host.parameters:
        return NO_DATA
    values = host.parameters[parameter_name]
    if parameter_name == 'ipAdEntAddr':
        values = filter(lambda x: x != '127.0.0.1', values)
        values = sorted(values)
        values = list(values)
    return ', '.join(values)


def make_report(hosts, report_file):
    hosts = sorted(hosts, key=lambda host: ','.join(host.parameters['hostLabel']))
    with xlsxwriter.Workbook(report_file) as workbook:
        worksheet = workbook.add_worksheet()
        header_format = workbook.add_format()
        header_format.set_bold()
        header_format.set_align('center')
        header_format.set_align('vcenter')
        header_format.set_border()

        leaf_columns = make_header(worksheet, columns_tree(), header_format, 2)

        for i, host in enumerate(hosts, 2):
            for j, column in enumerate(leaf_columns):
                worksheet.write(i, j, format_values(host, column.parameter_name))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir',
                        help='directory with report data files: hosts.tsv, links.tsv, vectors.tsv',
                        required=True)
    parser.add_argument('--report-file',
                        help='path to excel report file',
                        default='inventory.xlsx')
    args = parser.parse_args()

    started_at = dt.now()
    try:
        host_uuid_to_host = read_hosts(args.data_dir)
        uuid_to_aggregated_vector = read_aggregated_vectors(args.data_dir)
        links = read_links(args.data_dir)
        enrich_hosts_parameters(host_uuid_to_host, links, uuid_to_aggregated_vector,
                                AGGREGATED_VECTOR_PARAMETERS.keys())
        make_report(host_uuid_to_host.values(), args.report_file)
        sys.stderr.write("Done at " + str(dt.now() - started_at) + "\n")
        sys.stderr.write("Report available at " + os.path.abspath(args.report_file) + "\n")
    except Exception:
        sys.stderr.write("Failed:\n")
        traceback.print_exc()
        if os.path.exists(args.report_file):
            os.remove(args.report_file)
        exit(1)
