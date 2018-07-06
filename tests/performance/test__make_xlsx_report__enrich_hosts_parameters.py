import unittest
from examples.performance.make_xlsx_report import *

HOST1_UUID = 'af0f4429-6c21-4376-9d02-6895309a895a'
HOST2_UUID = '628734dc-aa36-40d8-a4e5-2f5ccabe781d'
HOST3_UUID = '5f3b6fc7-fdfa-45e2-89fd-9b7dfed0682c'
VECTOR12_UUID = '0820bf4d-a950-42a0-9d48-21084333595b'
VECTOR21_UUID = '68d0e8e2-0f5f-4ace-90a5-6bd478b6ca72'
VECTOR23_UUID = 'd3566308-cf99-4adf-986d-b6c1983ba473'
VECTOR32_UUID = 'e34eda96-6cf4-4467-926d-0b6f596fe8c6'
VECTOR3_UUID = '0af03445-9eca-440a-9fab-b7897a1e5178'
PARAMETER_NAME = 'level'


class MakeExcelReport_format_values_Tests(unittest.TestCase):
    def test_simple(self):
        host1 = Host(True, True)
        host2 = Host(True, True)
        host_uuid_to_host = {HOST1_UUID: host1, HOST2_UUID: host2}
        vector12 = aggregate_vector(PARAMETER_NAME, 10)
        vector21 = aggregate_vector(PARAMETER_NAME, 20)
        uuid_to_aggregated_vector = {VECTOR12_UUID: vector12, VECTOR21_UUID: vector21}
        links = [Link(HOST1_UUID, HOST2_UUID, VECTOR12_UUID, VECTOR21_UUID)]

        enrich_hosts_parameters(host_uuid_to_host, links, uuid_to_aggregated_vector, [PARAMETER_NAME])

        self.assertEqual(aggregate(10), host1.parameters[tx_aggregated_parameter_name(PARAMETER_NAME)])
        self.assertEqual(aggregate(20), host1.parameters[rx_aggregated_parameter_name(PARAMETER_NAME)])
        self.assertEqual(aggregate(20), host2.parameters[tx_aggregated_parameter_name(PARAMETER_NAME)])
        self.assertEqual(aggregate(10), host2.parameters[rx_aggregated_parameter_name(PARAMETER_NAME)])

    def test_plus_aggregate(self):
        host1 = Host(True, True)
        host2 = Host(True, True)
        host3 = Host(True, True)
        host_uuid_to_host = {HOST1_UUID: host1, HOST2_UUID: host2, HOST3_UUID: host3}
        vector12 = aggregate_vector(PARAMETER_NAME, 10)
        vector21 = aggregate_vector(PARAMETER_NAME, 20)
        vector23 = aggregate_vector(PARAMETER_NAME, 100)
        vector32 = aggregate_vector(PARAMETER_NAME, 200)
        uuid_to_aggregated_vector = {
            VECTOR12_UUID: vector12,
            VECTOR21_UUID: vector21,
            VECTOR23_UUID: vector23,
            VECTOR32_UUID: vector32}
        links = [
            Link(HOST1_UUID, HOST2_UUID, VECTOR12_UUID, VECTOR21_UUID),
            Link(HOST2_UUID, HOST3_UUID, VECTOR23_UUID, VECTOR32_UUID)]

        enrich_hosts_parameters(host_uuid_to_host, links, uuid_to_aggregated_vector, [PARAMETER_NAME])

        self.assertEqual(aggregate(10), host1.parameters[tx_aggregated_parameter_name(PARAMETER_NAME)])
        self.assertEqual(aggregate(20), host1.parameters[rx_aggregated_parameter_name(PARAMETER_NAME)])
        self.assertEqual(aggregate(20, 100), host2.parameters[tx_aggregated_parameter_name(PARAMETER_NAME)])
        self.assertEqual(aggregate(10, 200), host2.parameters[rx_aggregated_parameter_name(PARAMETER_NAME)])
        self.assertEqual(aggregate(200), host3.parameters[tx_aggregated_parameter_name(PARAMETER_NAME)])
        self.assertEqual(aggregate(100), host3.parameters[rx_aggregated_parameter_name(PARAMETER_NAME)])

    def test_absent_vector_parameter(self):
        host1 = Host(True, True)
        host2 = Host(True, True)
        host_uuid_to_host = {HOST1_UUID: host1, HOST2_UUID: host2}
        vector12 = aggregate_vector(PARAMETER_NAME, 10)
        vector21 = AggregatedVector()
        uuid_to_aggregated_vector = {VECTOR12_UUID: vector12, VECTOR21_UUID: vector21}
        links = [Link(HOST1_UUID, HOST2_UUID, VECTOR12_UUID, VECTOR21_UUID)]

        enrich_hosts_parameters(host_uuid_to_host, links, uuid_to_aggregated_vector, [PARAMETER_NAME])

        self.assertEqual(aggregate(10), host1.parameters[tx_aggregated_parameter_name(PARAMETER_NAME)])
        self.assertEqual(aggregate(), host1.parameters[rx_aggregated_parameter_name(PARAMETER_NAME)])
        self.assertEqual(aggregate(), host2.parameters[tx_aggregated_parameter_name(PARAMETER_NAME)])
        self.assertEqual(aggregate(10), host2.parameters[rx_aggregated_parameter_name(PARAMETER_NAME)])

def aggregate_vector(parameter_name, value):
    vector = AggregatedVector()
    vector.plus_parameter_value(parameter_name, value)
    return vector


def aggregate(*values):
    aggregate = AggregatedParameter()
    for value in values:
        aggregate.plus(value)
    return aggregate


if __name__ == '__main__':
    unittest.main()
