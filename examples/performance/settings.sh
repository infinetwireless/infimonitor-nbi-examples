#! /usr/bin/env bash
set -euo pipefail

# All paths variables are related to directory where this script is localed
SCRIPT_DIR=$(dirname "$(realpath "$0")")

REPORT_NAME=inventory

# A default date-time window of the loaded parameters history. Last month by default,
FROM=$(date --date='-1 month' '+%Y-%m-01T00:00%:z')
TO=$(date                   '+%Y-%m-01T00:00%:z')
# or can be specified manually as something like:
# FROM=2017-06-01T00:00:00.000+05:00
# TO=2017-07-01T00:00:00.000+05:00

# A default output files directory. It is specified as a last month like ../out/2017-06
LAST_MONTH=$(date --date='-1 month' '+%Y-%m')
OUT_DIR=${SCRIPT_DIR}/../../out/${REPORT_NAME}/${LAST_MONTH}
# or can be specified manually:
# OUT_DIR=$SCRIPT_DIR/../../out/2017-06
