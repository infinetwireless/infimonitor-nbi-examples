import sys
import json
import requests
import itertools
import csv
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from collections import OrderedDict
import argparse
import urllib
import re


def reencode_query_string(url):
    def reassemble(matches):
        url_base, query, fragment = matches.group(1), matches.group(2), matches.group(3)
        result = url_base
        if query:
            def name_value(str):
                return str.split("=", 1)

            result += query[:1]
            parameters = {name: value for name, value in map(name_value, query[1:].split("&"))}
            result += urllib.parse.urlencode(parameters)
        if fragment:
            result += fragment
        return result

    return re.sub('([^?]+)([^#]+)?(.+)?', reassemble, url)


def get_json(token, url, params):
    response = requests.get(url,
                            params=params,
                            headers={
                                'x-auth-token': token,
                                'Accept': 'application/json'},
                            verify=False)
    response.raise_for_status()
    return response.json(object_pairs_hook=OrderedDict)


def json_item_to_row(json_item, column_names):
    def extract_json_item_attribute(name):
        value = json_item[name]
        return value if isinstance(value, str) else json.dumps(value)

    return list(map(extract_json_item_attribute, column_names))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='https://localhost/api/nbi/v1.beta/vectors/all/history',
                        help='REST API entry point URL')
    parser.add_argument('--token', required=True, help='REST API token')
    parser.add_argument('--file', help='Path to the tsv file otherwise stdout will be used')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--page-size', type=int, default="1024",
                       help='Number of JSON objects in a single HTTP response')
    group.add_argument('--quantity-of-parts', type=int,
                       help='Number of JSON objects in a single HTTP response')
    args = parser.parse_args()

    url = reencode_query_string(args.url)

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    with open(args.file, 'w') if args.file else sys.stdout as file:
        writer = csv.writer(file, dialect='excel-tab', lineterminator='\n')
        if args.quantity_of_parts:
            paging = False
            parameters_stream = map(lambda x: {'part': x, 'ofParts': args.quantity_of_parts},
                                    range(args.quantity_of_parts))
        else:
            paging = True
            parameters_stream = map(lambda x: {'page': x, 'size': args.page_size}, itertools.count())

        column_names = None
        for parameters in parameters_stream:
            json_items = get_json(args.token, url, parameters)
            if not column_names and json_items:
                column_names = list(json_items[0].keys())
                writer.writerow(column_names)
            for json_item in json_items:
                writer.writerow(json_item_to_row(json_item, column_names))
            if paging and len(json_items) != args.page_size:
                break
