import unittest
from examples.inventory.make_xlsx_report import *

IFACE_UUID = '079a412a-e77f-423e-a986-583cb6345626'
PRF_IFACE_UUID = '08dbb75a-677e-4785-9bf0-bc255b756979'

class MakeExcelReport_format_values_Tests(unittest.TestCase):
    def test_hostLabel_when_host_is_exists_and_activated(self):
        host = Host(True, True)
        host.add_parameter_value('hostLabel', 'Host1')

        result = format_values(host, 'hostLabel')

        self.assertEqual('Host1', result)

    def test_hostLabel_when_host_is_not_exists_and_not_activated(self):
        host = Host(False, False)
        host.add_parameter_value('hostLabel', 'Host1')

        result = format_values(host, 'hostLabel')

        self.assertEqual('Host1 (deleted)', result)

    def test_hostLabel_when_host_is_exists_but_not_activated(self):
        host = Host(True, False)
        host.add_parameter_value('hostLabel', 'Host1')

        result = format_values(host, 'hostLabel')

        self.assertEqual('Host1 (no license)', result)

    def test_hostLabel_when_host_is_not_exists_but_activated(self):
        host = Host(False, True)
        host.add_parameter_value('hostLabel', 'Host1')
        result = format_values(host, 'hostLabel')

        self.assertEqual('Host1 (deleted)', result)

    def test_ipAdEntAddr_filterout_localhost(self):
        host = Host(True, True)
        host.add_iface_parameter_value(IFACE_UUID, 'ipAdEntAddr', '1.68.2.10')
        host.add_iface_parameter_value(IFACE_UUID, 'ipAdEntAddr', '127.0.0.1')
        host.add_iface_parameter_value(IFACE_UUID, 'ipAdEntAddr', '192.168.0.10')

        result = format_values(host, 'ipAdEntAddr')

        self.assertEqual('1.68.2.10, 192.168.0.10', result)

    def test_BANDWIDTH_not_XG(self):
        host = Host(True, True)
        host.add_parameter_value('productFamily', 'X123')
        host.add_parameter_value('rmBandwidth', '20')

        result = format_values(host, BANDWIDTH)

        self.assertEqual(20, result)

    def test_BANDWIDTH_XG(self):
        host = Host(True, True)
        host.add_parameter_value('productFamily', 'XG')
        host.add_parameter_value('xgChannelWidth', 'BAND_20_MHZ')

        result = format_values(host, BANDWIDTH)

        self.assertEqual(20, result)

    def test_prf_interfaces_filter_out_rmBandwidth(self):
        host = Host(True, True)
        host.add_parameter_value('productFamily', 'X123')
        host.add_iface_parameter_value(IFACE_UUID, 'ifDescr', 'rf.0')
        host.add_iface_parameter_value(IFACE_UUID, 'rmBandwidth', '20')
        host.add_iface_parameter_value(PRF_IFACE_UUID, 'ifDescr', 'prf.0')
        host.add_iface_parameter_value(PRF_IFACE_UUID, 'rmBandwidth', '0')

        result = format_values(host, BANDWIDTH)

        self.assertEqual(20, result)

    def test_prf_interfaces_filter_out_rmFrequency(self):
        host = Host(True, True)
        host.add_iface_parameter_value(IFACE_UUID, 'ifDescr', 'rf.0')
        host.add_iface_parameter_value(IFACE_UUID, 'rmFrequency', '5340')
        host.add_iface_parameter_value(PRF_IFACE_UUID, 'ifDescr', 'prf.0')
        host.add_iface_parameter_value(PRF_IFACE_UUID, 'rmFrequency', '0')

        result = format_values(host, 'rmFrequency')

        self.assertEqual(5340, result)

    def test_prf_interfaces_ipAdEntAddr(self):
        host = Host(True, True)
        host.add_iface_parameter_value(IFACE_UUID, 'ipAdEntAddr', '1.68.3.26')
        host.add_iface_parameter_value(IFACE_UUID, 'ipAdEntAddr', '1.68.3.27')
        host.add_iface_parameter_value(PRF_IFACE_UUID, 'ipAdEntAddr', '192.68.3.26')
        host.add_iface_parameter_value(PRF_IFACE_UUID, 'ipAdEntAddr', '192.68.3.27')

        result = format_values(host, 'ipAdEntAddr')

        self.assertEqual('1.68.3.26, 1.68.3.27, 192.68.3.26, 192.68.3.27', result)


if __name__ == '__main__':
    unittest.main()
