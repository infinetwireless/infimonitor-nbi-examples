#! /usr/bin/env bash
set -euo pipefail

# All paths variables are related to directory where this script is localed
SCRIPT_DIR=$(dirname "$(realpath "$0")")

REPORT_NAME=performance

# A date-time window of the loaded parameters history. Last full day i.e. yesterday by default,
FROM=$(date --date='-1 day' '+%Y-%m-%dT00:00%:z')
TO=$(date                   '+%Y-%m-%dT00:00%:z')
# or can be specified manually as something like:
# FROM=2017-06-01T00:00:00.000+05:00
# TO=2017-07-01T00:00:00.000+05:00

# An output files directory. It is specified as a last full day i.e. yesterday like .../2018-07-04
YESTERDAY=$(date --date='-1 day' '+%Y-%m-%d')
OUT_DIR=${SCRIPT_DIR}/../../out/${REPORT_NAME}/${YESTERDAY}
# or can be specified manually:
# OUT_DIR=$SCRIPT_DIR/../../out/performance/2018-07-04

# Specifies where to find imported modules for python scripts
export PYTHONPATH="$(realpath "${SCRIPT_DIR}/../..")"
