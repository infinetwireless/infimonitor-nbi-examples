from examples.performance.make_xlsx_report import *

R5000_AGGREGATED_COLUMNS_PROTOTYPES = [
    ColumnPrototype('Rx Level dB', IntParameter('currentLevel')),
    ColumnPrototype('Tx retries %', IntParameter('retries')),
    ColumnPrototype('Tx bitrate Mbps', IntParameter('bitrate'))]

XG_AGGREGATED_COLUMNS_PROTOTYPES = [
    ColumnPrototype('CINR dBm', IntParameter('xgCINR')),
    ColumnPrototype('absolute RSSI dBm', IntParameter('xgABSRSSI')),
    ColumnPrototype('total Tx capacity Mbps', FixedPointParameter('xgTotalCapacityTx', 100))]


def columns_tree(aggregated_columns_prototypes):
    def create_formatter(host_to_vectors, parameter, aggregated_value_transform):
        return lambda host: format_vectors(host_to_vectors(host), parameter, aggregated_value_transform)

    def out_vectors(host):
        return host.out_vectors

    def in_vectors(host):
        return host.in_vectors

    columns = [Column('Host name', lambda host: host.label(), 15),
               Column('IP address', lambda host: host.ips(), 25)]
    for prototype in aggregated_columns_prototypes:
        column_display_name, parameter = prototype.column_display_name, prototype.parameter
        width = 8
        columns.append(
            Column('{0}'.format(column_display_name), sub_columns=[
                Column('Avg', create_formatter(out_vectors, parameter, aggregated_avg), width),
                Column('Min', create_formatter(out_vectors, parameter, aggregated_min), width),
                Column('Max', create_formatter(out_vectors, parameter, aggregated_max), width)]))
        columns.append(
            Column('??? {0}'.format(column_display_name), sub_columns=[
                Column('Avg', create_formatter(in_vectors, parameter, aggregated_avg), width),
                Column('Min', create_formatter(in_vectors, parameter, aggregated_min), width),
                Column('Max', create_formatter(in_vectors, parameter, aggregated_max), width)]))
    return Column(None, sub_columns=columns)


def format_vectors(vectors, parameter, aggregated_value_transform):
    if not vectors:
        return NO_DATA
    vectors_values = map(lambda vector: format_vector(vector, parameter, aggregated_value_transform), vectors)
    vectors_values = list(vectors_values)
    if len(vectors_values) < 1:
        return NO_DATA
    if len(vectors_values) == 1:
        return vectors_values[0]
    return ', '.join(map(lambda value: str(value), vectors_values))


def enrich_hosts(uuid_to_host, links, uuid_to_aggregated_vector):
    for host in uuid_to_host.values():
        host.out_vectors = []
        host.in_vectors = []
    for link in links:
        host_a = uuid_to_host.get(link.host_a_uuid)
        host_b = uuid_to_host.get(link.host_b_uuid)
        aggregated_vector_a = uuid_to_aggregated_vector.get(link.vector_a_uuid)
        aggregated_vector_b = uuid_to_aggregated_vector.get(link.vector_b_uuid)
        if host_a:
            host_a.out_vectors.append(aggregated_vector_a)
            host_a.in_vectors.append(aggregated_vector_b)
        if host_b:
            host_b.out_vectors.append(aggregated_vector_b)
            host_b.in_vectors.append(aggregated_vector_a)


class HostsView:
    def __init__(self, name, aggregated_columns_prototypes, filter):
        self.name = name
        self.aggregated_columns_prototypes = aggregated_columns_prototypes
        self.filter = filter


def make_report(data_dir, report_file):
    views = [HostsView("R5000 radio", R5000_AGGREGATED_COLUMNS_PROTOTYPES, lambda host: not host.is_xg()),
             HostsView("XG radio", XG_AGGREGATED_COLUMNS_PROTOTYPES, lambda host: host.is_xg())]
    name_to_parameter = {prototype.parameter.name: prototype.parameter
                         for view in views
                         for prototype in view.aggregated_columns_prototypes}

    with xlsxwriter.Workbook(report_file) as workbook:
        header_format = workbook.add_format()
        header_format.set_bold()
        header_format.set_align('center')
        header_format.set_align('vcenter')
        header_format.set_border()

        host_uuid_to_host = read_hosts(data_dir)
        uuid_to_aggregated_vector = read_aggregated_vectors(data_dir, name_to_parameter)
        links = read_links(data_dir)
        enrich_hosts(host_uuid_to_host, links, uuid_to_aggregated_vector)

        for view in views:
            worksheet = workbook.add_worksheet(view.name)
            view_hosts = host_uuid_to_host.values()
            view_hosts = filter(view.filter, view_hosts)
            view_hosts = list(view_hosts)
            view_hosts = sorted(view_hosts, key=lambda host: host.label())
            view_columns_tree = columns_tree(view.aggregated_columns_prototypes)
            leaf_columns = make_header(worksheet, view_columns_tree, header_format, 2)
            for i, host in enumerate(view_hosts, 2):
                for j, column in enumerate(leaf_columns):
                    worksheet.write(i, j, column.format_values(host))


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
