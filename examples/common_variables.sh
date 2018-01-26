#!/bin/sh

# All paths variables are related to directory where this script is localed
SCRIPT_DIR=$(dirname "$(realpath $0)")

# A default date-time window of the loaded parameters history. Last month by default,
export DEFAULT_FROM=`date --date='-1 month' +%Y-%m-01T00:00%:z`
DEFAULT_TO=`date                   +%Y-%m-01T00:00%:z`
# or can be specified manually as something like:
# DEFAULT_FROM=2017-06-01T00:00:00.000+05:00
# DEFAULT_TO=2017-07-01T00:00:00.000+05:00

# A default output files directory. It is specified as a last month like ../out/2017-06
LAST_MONTH=`date --date='-1 month' +%Y-%m`
DEFAULT_OUT_DIR=$SCRIPT_DIR/../out/$LAST_MONTH
# or can be specified manually:
# DEFAULT_OUT_DIR=$SCRIPT_DIR/../out/2017-06
