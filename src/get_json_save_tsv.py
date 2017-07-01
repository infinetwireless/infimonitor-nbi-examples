import sys

if (sys.version_info < (3, 5)):    
    raise Exception('Python 3.5 required, but current version is ' + sys.version)

import json
import requests
import itertools
import csv
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from collections import OrderedDict
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--url', default = 'https://localhost/api/nbi/v1.beta/vectors/all/history', help = 'REST API URL')
parser.add_argument('--token', required = True, help = 'REST API token')
parser.add_argument('--file', required = True, help='Path to the tsv file')
args = parser.parse_args()

PAGE_SIZE = 1024*16

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def get_json(page, size):
    response = requests.get(args.url,
        params = {'page': page, 'size': size},
        headers = {
            'x-auth-token': args.token,
            'Accept': 'application/json'},
        verify = False)
    response.raise_for_status()
    return response.json(object_pairs_hook = OrderedDict)


def item_to_row(item, column_names):

    def extract_value(column_name):
        value = item[column_name]
        return value if isinstance(value, str) else json.dumps(value)

with open(args.file, 'w') as f:
	writer = csv.writer(f, dialect = 'excel-tab', lineterminator='\n')
	columnNames = None
	for page in itertools.count():
		items = get_json(page, PAGE_SIZE)
		if not columnNames and items: 
			columnNames = items[0].keys()
			writer.writerow(columnNames)
		for item in items:            
			writer.writerow(item_to_row(item, columnNames))
		if len(items) < PAGE_SIZE:
			break