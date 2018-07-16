from examples.performance.make_xlsx_report import *

HOSTS_IDENTIFYING_COLUMNS = [
    Column('Host name', StringParameter('hostLabel'), 15),
    Column('IP address', StringParameter('ipAdEntAddr'), 25)]

def enrich_hosts_parameters(uuid_to_host, parameters, links, uuid_to_aggregated_vector):
    for link in links:
        if link.host_a_uuid not in uuid_to_host or \
                link.host_b_uuid not in uuid_to_host or \
                link.vector_a_uuid not in uuid_to_aggregated_vector or \
                link.vector_b_uuid not in uuid_to_aggregated_vector:
            continue  # hosts, links and vectors are loaded separately so they may be a bit inconsistent
        host_a = uuid_to_host[link.host_a_uuid]
        host_b = uuid_to_host[link.host_b_uuid]
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


class HostsView:
    def __init__(self, name, aggregated_columns, filter):
        self.name = name
        self.aggregated_columns = aggregated_columns
        self.aggregated_parameters = list(map(lambda column: column.parameter, aggregated_columns))
        self.filter = filter


def make_report(data_dir, report_file):
    views = [HostsView("R5000 radio", AGGREGATED_COLUMNS_R5000,
                       lambda host: host.parameters['productFamily'] != ['XG']),
             HostsView("XG radio", AGGREGATED_COLUMNS_XG,
                       lambda host: host.parameters['productFamily'] == ['XG'])]
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
        enrich_hosts_parameters(host_uuid_to_host, name_to_parameter.values(), links, uuid_to_aggregated_vector)

        for view in views:
            worksheet = workbook.add_worksheet(view.name)
            hosts = host_uuid_to_host.values()
            hosts = filter(view.filter, hosts)
            hosts = list(hosts)
            hosts = sorted(hosts, key=lambda host: ','.join(host.parameters['hostLabel']))
            view_columns_tree = columns_tree(HOSTS_IDENTIFYING_COLUMNS, view.aggregated_columns)
            leaf_columns = make_header(worksheet, view_columns_tree, header_format, 2)
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
