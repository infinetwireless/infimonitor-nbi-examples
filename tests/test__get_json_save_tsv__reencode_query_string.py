import unittest
from examples.get_json_save_tsv import reencode_query_string


class GetJSONSaveTSV_ReencodeQueryString_Tests(unittest.TestCase):
    def test_no_query_no_fragment(self):
        url = 'https://localhost:8080/api'

        result = reencode_query_string(url)

        self.assertEqual(result, url)

    def test_no_query_but_with_fragment(self):
        url = 'https://localhost:8080/api#tag'

        result = reencode_query_string(url)

        self.assertEqual(result, url)

    def test_with_query_but_no_fragment(self):
        url = 'https://localhost:8080/api?param=value'

        result = reencode_query_string(url)

        self.assertEqual(result, url)

    def test_with_query_and_with_fragment(self):
        url = 'https://localhost:8080/api?param=value#tag'

        result = reencode_query_string(url)

        self.assertEqual(result, url)

    def test_encode_query(self):
        url = 'https://localhost:8080/api?param=v a+l-u\te'

        result = reencode_query_string(url)

        self.assertEqual(result, "https://localhost:8080/api?param=v+a%2Bl-u%09e")

if __name__ == '__main__':
    unittest.main()
