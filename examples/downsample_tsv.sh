#!/bin/sh

# All paths variables are related to directory where this script is localed
SCRIPT_DIR=$(dirname "$(realpath $0)")

# Initialize common variables in a single place
. "$SCRIPT_DIR/common_variables.sh"

# Input and output files. By default they are located in a last month named directory like ../out/2017-06
INPUT=$DEFAULT_OUT_DIR/vectors_history.tsv
OUTPUT=$DEFAULT_OUT_DIR/downsampled_vectors_history.tsv
# or can be specified manually as something like:
# INPUT=$SCRIPT_DIR/../out/2017-06/vectors_history.tsv
# OUTPUT=$SCRIPT_DIR/../out/2017-06/downsampled_vectors_history.tsv

# The target number of points in a series
DOWNSAMPLE_TO=100

# Specifies where to find imported modules for python scripts
export "PYTHONPATH=$SCRIPT_DIR/.."

cat "$INPUT" | python3 "$SCRIPT_DIR/downsample_tsv.py" --downsample-to $DOWNSAMPLE_TO > "$OUTPUT"