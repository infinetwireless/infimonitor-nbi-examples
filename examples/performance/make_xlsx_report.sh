#! /usr/bin/env bash
set -euo pipefail

# All paths variables are related to directory where this script is localed
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Initialize common variables in a single place
. "${SCRIPT_DIR}/settings.sh"

python3 "${SCRIPT_DIR}/make_xlsx_report.py" \
  --data-dir "${OUT_DIR}" \
  --report-file "${OUT_DIR}/${REPORT_NAME}.xlsx"
