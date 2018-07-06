import argparse
import csv
from datetime import datetime as dt
from collections import OrderedDict
import os
import re
import sys
import traceback
import xlsxwriter

IS_FLOAT_REGEXP = re.compile('^\d+(\.\d+)?$')
BANDWIDTH = 'BANDWIDTH'


class Interface:
    def __init__(self):
        self.parameters = {}


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

    def add_iface_parameter_value(self, iface_uuid, parameter_name, parameter_value):
        if iface_uuid not in self.interfaces:
            self.interfaces[iface_uuid] = Interface()
        iface = self.interfaces[iface_uuid]
        if parameter_name not in iface.parameters:
            iface.parameters[parameter_name] = []  # some interface parameters can be multivalued
        iface.parameters[parameter_name].append(parameter_value)


class Column:
    def __init__(self, header, width=None):
        self.header = header
        self.width = width


def read_hosts(data_dir):
    host_uuid_to_host = {}
    with open(data_dir + '/hosts.tsv', 'rt') as file:
        reader = csv.reader(file, dialect='excel-tab')
        next(reader, None)  # skip headers
        for host_uuid, exists, activated in reader:
            host_uuid_to_host[host_uuid] = Host(exists.lower() == 'true', activated.lower() == 'true')

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
            host.add_iface_parameter_value(iface_uuid, parameter_name, value)

    return host_uuid_to_host.values()


def format_values(host, parameter_name):
    def format_host_values():
        values = host.parameters[parameter_name]
        if parameter_name == 'hostLabel':
            if not host.exists:
                values = [values[0] + ' (deleted)']
            elif not host.activated:
                values = [values[0] + ' (no license)']
        if parameter_name == 'xgChannelWidth':
            values = map(lambda x: x.replace('BAND_', '').replace('_MHZ', ''), values)
            values = list(values)
        return values

    def format_ifaces_values():
        values = []
        for iface in host.interfaces.values():
            if parameter_name in ['rmBandwidth', 'rmFrequency'] and iface.parameters['ifDescr'][0].startswith("prf"):
                continue
            if parameter_name in iface.parameters:
                values.extend(iface.parameters[parameter_name])
        if parameter_name == 'ipAdEntAddr':
            values = filter(lambda x: x != '127.0.0.1', values)
            values = sorted(values)
            values = list(values)
        return values

    if parameter_name == BANDWIDTH:
        if host.parameters['productFamily'][0] == 'XG':
            return format_values(host, 'xgChannelWidth')
        else:
            return format_values(host, 'rmBandwidth')
    elif parameter_name in host.parameters:
        values = format_host_values()
    else:
        values = format_ifaces_values()
    if not values:
        return '-'
    if len(values) == 1 and IS_FLOAT_REGEXP.match(values[0]):
        return float(values[0])
    return ', '.join(values)


def make_report(hosts, report_file):
    parameter_to_column = OrderedDict([
        ('hostLabel', Column('Host name', 20)),
        ('ipAdEntAddr', Column('IP address', 60)),
        ('productFamily', Column('Product family', 15)),
        ('sysSerialNumber', Column('Serial number', 15)),
        ('sysSoftwareVersion', Column('Software version', 15)),
        ('sysModel', Column('Model', 25)),
        (BANDWIDTH, Column('Bandwidth MHz', 15)),
        ('rmFrequency', Column('Frequency MHz', 15))])

    hosts = sorted(hosts, key=lambda host: ','.join(host.parameters['hostLabel']))
    with xlsxwriter.Workbook(report_file) as workbook:
        worksheet = workbook.add_worksheet()
        worksheet.freeze_panes(1, 0)

        bold = workbook.add_format({'bold': True})
        for i, (_, column) in enumerate(parameter_to_column.items()):
            worksheet.write(0, i, column.header, bold)
            if column.width:
                worksheet.set_column(i, i, column.width)
        for i, host in enumerate(hosts, 1):
            for j, (parameter_name, _) in enumerate(parameter_to_column.items()):
                worksheet.write(i, j, format_values(host, parameter_name))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir',
                        help='directory with report data files: hosts.tsv, links.tsv, vectors.tsv',
                        required=True)
    parser.add_argument('--report-file',
                        help='path to xlsx report file',
                        default='inventory.xlsx')
    args = parser.parse_args()

    started_at = dt.now()
    try:
        hosts = read_hosts(args.data_dir)
        make_report(hosts, args.report_file)
        sys.stderr.write("Done at " + str(dt.now() - started_at) + "\n")
        sys.stderr.write("Report available at " + os.path.abspath(args.report_file) + "\n")
    except Exception:
        sys.stderr.write("Failed:\n")
        traceback.print_exc()
        if os.path.exists(args.report_file):
            os.remove(args.report_file)
        exit(1)
