import argparse
import csv
from datetime import datetime as dt
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


class AggregatedParameter:
    def __init__(self, name, inner_to_xlsx_value_function):
        self.name = name
        self.inner_to_xlsx_value_function = inner_to_xlsx_value_function

    def inner_to_xlsx_value(self, value):
        return self.inner_to_xlsx_value_function(value)


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

    def aggregate_other(self, other):
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


class Column:
    def __init__(self, display_name, parameter=None, width=None, sub_columns=[]):
        self.display_name = display_name
        self.parameter = parameter
        self.width = width
        self.sub_columns = sub_columns


AGGREGATED_COLUMNS_R5000 = [
    Column('Level dB', IntParameter('currentLevel')),
    Column('Retries %', IntParameter('retries')),
    Column('Bitrate Mbps', IntParameter('bitrate'))]

AGGREGATED_COLUMNS_XG = [
    Column('CINR dBm', IntParameter('xgCINR')),
    Column('Absolute RSSI dBm', IntParameter('xgABSRSSI')),
    Column('Total capacity Mbps', FixedPointParameter('xgTotalCapacityTx', 100))]


def columns_tree(aggregated_columns):
    columns = [
        Column('Host name', StringParameter('hostLabel'), 15),
        Column('IP address', StringParameter('ipAdEntAddr'), 25)]

    for column in aggregated_columns:
        rx_parameter_name = rx_aggregated_parameter_name(column.parameter)
        tx_parameter_name = tx_aggregated_parameter_name(column.parameter)
        avg = lambda column, aggregated_value: float(int(
            column.parameter.inner_to_xlsx_value(100 * aggregated_value.sum / aggregated_value.count))) / 100
        min = lambda column, aggregated_value: column.parameter.inner_to_xlsx_value(aggregated_value.min)
        max = lambda column, aggregated_value: column.parameter.inner_to_xlsx_value(aggregated_value.max)

        def partial(aggregating_function, column):  # put column in a produced function scope
            return lambda aggregated_value: aggregating_function(column, aggregated_value)

        width = 8
        columns.append(
            Column('Rx {0}'.format(column.display_name), sub_columns=[
                Column('Avg', AggregatedParameter(rx_parameter_name, partial(avg, column)), width),
                Column('Min', AggregatedParameter(rx_parameter_name, partial(min, column)), width),
                Column('Max', AggregatedParameter(rx_parameter_name, partial(max, column)), width)]))
        columns.append(
            Column('Tx {0}'.format(column.display_name), sub_columns=[
                Column('Avg', AggregatedParameter(tx_parameter_name, partial(avg, column)), width),
                Column('Min', AggregatedParameter(tx_parameter_name, partial(min, column)), width),
                Column('Max', AggregatedParameter(tx_parameter_name, partial(max, column)), width)]))
    return Column(None, None, sub_columns=columns)


def tx_aggregated_parameter_name(parameter):
    return 'TX_{0}'.format(parameter.name.upper())


def rx_aggregated_parameter_name(parameter):
    return 'RX_{0}'.format(parameter.name.upper())


class Host:
    def __init__(self, exists, activated):
        self.exists = exists
        self.activated = activated
        self.parameters = {}

    def append_parameter_value(self, parameter_name, parameter_value):
        if parameter_name not in self.parameters:
            self.parameters[parameter_name] = []  # some parameters can be multivalued, like IP address
        self.parameters[parameter_name].append(parameter_value)


class Link:
    def __init__(self, host_a_uuid, host_b_uuid, vector_a_uuid, vector_b_uuid):
        self.host_a_uuid = host_a_uuid
        self.host_b_uuid = host_b_uuid
        self.vector_a_uuid = vector_a_uuid
        self.vector_b_uuid = vector_b_uuid


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
                continue  # hosts_interfaces and interfaces parameters are loaded separately so they may be a bit inconsistent
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
    with open(data_dir + '/links.tsv', 'rt') as file:
        reader = csv.reader(file, dialect='excel-tab')
        next(reader, None)  # skip headers
        links = []
        for _, _, _, host_a_uuid, host_b_uuid, _, _, vector_a_uuid, vector_b_uuid in reader:
            links.append(Link(host_a_uuid, host_b_uuid, vector_a_uuid, vector_b_uuid))
        return links


def enrich_hosts_parameters(host_uuid_to_host, links, uuid_to_aggregated_vector, parameters):
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
        for parameter in parameters:
            tx_parameter_name = tx_aggregated_parameter_name(parameter)
            rx_parameter_name = rx_aggregated_parameter_name(parameter)

            aggregated_vector_a_parameter = aggregated_vector_a.parameters.get(parameter.name, [])
            aggregated_vector_b_parameter = aggregated_vector_b.parameters.get(parameter.name, [])

            host_a.append_parameter_value(tx_parameter_name, aggregated_vector_a_parameter)
            host_a.append_parameter_value(rx_parameter_name, aggregated_vector_b_parameter)
            host_b.append_parameter_value(tx_parameter_name, aggregated_vector_b_parameter)
            host_b.append_parameter_value(rx_parameter_name, aggregated_vector_a_parameter)


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


class HostsView:
    def __init__(self, name, aggregated_columns, filter):
        self.name = name
        self.aggregated_columns = aggregated_columns
        self.aggregated_parameters = list(map(lambda column: column.parameter, aggregated_columns))
        self.filter = filter


def make_report(data_dir, report_file):
    views = [HostsView("R5000", AGGREGATED_COLUMNS_R5000, lambda host: host.parameters['productFamily'] != ['XG']),
             HostsView("XG", AGGREGATED_COLUMNS_XG, lambda host: host.parameters['productFamily'] == ['XG'])]
    name_to_parameter = {parameter.name: parameter for view in views for parameter in view.aggregated_parameters}

    with xlsxwriter.Workbook(report_file) as workbook:
        header_format = workbook.add_format()
        header_format.set_bold()
        header_format.set_align('center')
        header_format.set_align('vcenter')
        header_format.set_border()

        host_uuid_to_host = read_hosts(data_dir)
        uuid_to_aggregated_vector = read_aggregated_vectors(data_dir, name_to_parameter)
        links = read_links(data_dir)
        enrich_hosts_parameters(host_uuid_to_host, links, uuid_to_aggregated_vector, name_to_parameter.values())

        for view in views:
            worksheet = workbook.add_worksheet(view.name)
            hosts = host_uuid_to_host.values()
            hosts = filter(view.filter, hosts)
            hosts = list(hosts)
            hosts = sorted(hosts, key=lambda host: ','.join(host.parameters['hostLabel']))
            leaf_columns = make_header(worksheet, columns_tree(view.aggregated_columns), header_format, 2)
            for i, host in enumerate(hosts, 2):
                for j, column in enumerate(leaf_columns):
                    worksheet.write(i, j, format_values(column, host))


def format_values(column, host):
    if column.parameter.name not in host.parameters:
        return NO_DATA
    values = host.parameters[column.parameter.name]
    if values is None:
        return NO_DATA

    if column.parameter.name == 'ipAdEntAddr':
        values = sorted(filter(lambda x: x != '127.0.0.1', values))
    if type(column.parameter) is AggregatedParameter:
        new_values = []
        for sub_values in values:
            if len(sub_values) > 0:
                new_values.append(max(map(column.parameter.inner_to_xlsx_value, sub_values)))
        values = new_values
    values = list(values)
    if len(values) == 0:
        return NO_DATA
    if len(values) == 1:
        return values[0]
    return ', '.join(map(lambda x: str(x), values))


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
        make_report(args.data_dir, args.report_file)
        sys.stderr.write("Done at " + str(dt.now() - started_at) + "\n")
        sys.stderr.write("Report available at " + os.path.abspath(args.report_file) + "\n")
    except Exception:
        sys.stderr.write("Failed:\n")
        traceback.print_exc()
        if os.path.exists(args.report_file):
            os.remove(args.report_file)
        exit(1)
