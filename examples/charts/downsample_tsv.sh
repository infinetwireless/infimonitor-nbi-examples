#! /usr/bin/env bash
set -euo pipefail

# All paths variables are related to directory where this script is localed
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Initialize script variables in a single place
. "${SCRIPT_DIR}/settings.sh"

python3 "$SCRIPT_DIR/downsample_tsv.py" \
  --input "${OUT_DIR}/vectors_history.tsv" \
  --downsample-to ${DOWNSAMPLE_TO} \
  --estimate-progress \
  > "${OUT_DIR}/downsampled_vectors_history.tsv"