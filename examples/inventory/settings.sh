#! /usr/bin/env bash
set -euo pipefail

# All paths variables are related to directory where this script is localed
SCRIPT_DIR=$(dirname "$(realpath "$0")")

REPORT_NAME=inventory

# A default output files directory. It is specified as a current date like .../2018-06-27
TODAY=$(date '+%Y-%m-%d')
OUT_DIR=${SCRIPT_DIR}/../../out/${REPORT_NAME}/${TODAY}
# or can be specified manually:
# OUT_DIR=$SCRIPT_DIR/../../out/inventory/2018-06-27

# Specifies where to find imported modules for python scripts
export PYTHONPATH="$(realpath "${SCRIPT_DIR}/../..")"
