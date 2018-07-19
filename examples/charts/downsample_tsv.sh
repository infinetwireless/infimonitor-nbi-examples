#! /usr/bin/env bash
set -euo pipefail

# All paths variables are related to directory where this script is localed
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Initialize script variables in a single place
. "${SCRIPT_DIR}/settings.sh"

# Input and output files. By default they are located in a last month named directory like ../out/2017-06
INPUT=${OUT_DIR}/vectors_history.tsv
OUTPUT=${OUT_DIR}/downsampled_vectors_history.tsv
# or can be specified manually as something like:
# INPUT=${SCRIPT_DIR}/../out/2017-06/vectors_history.tsv
# OUTPUT=${SCRIPT_DIR}/../out/2017-06/downsampled_vectors_history.tsv

python3 "$SCRIPT_DIR/downsample_tsv.py" \
  --input "$INPUT" \
  --downsample-to ${DOWNSAMPLE_TO} \
  --estimate-progress \
  > "$OUTPUT"