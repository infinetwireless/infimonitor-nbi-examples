import sys
import argparse
import datetime as dt
from dateutil.relativedelta import relativedelta
import re

parser = argparse.ArgumentParser()
parser.add_argument('--delta-days', type=int, default='0')
parser.add_argument('--delta-months', type=int, default='0')
parser.add_argument('--format', default='%Y.%m.%dT%H:%M:%S%:z')
args = parser.parse_args()

datetime = dt.datetime.now().astimezone() + dt.timedelta(days=args.delta_days) + relativedelta(months=args.delta_months)

format_with_hack = args.format.replace('%:z', '@%z@')
result = datetime.strftime(format_with_hack)
result = re.sub('([^@]*)@(.\d\d)(\d\d)@([^@]*)', '\g<1>\g<2>:\g<3>\g<4>', result)
sys.stdout.write(result)
