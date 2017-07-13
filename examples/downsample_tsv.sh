#!/bin/sh

# All paths variables are related to directory where this script is localed
SCRIPT_DIR=$(dirname $(realpath $0))

# Input and output files. By default they are located in a last month named directory like ../out/2017-06
# They can be specified manually as something like:
# INPUT=$SCRIPT_DIR/../out/2017-06/vectors.tsv
# OUTPUT=$SCRIPT_DIR/../out/2017-06/downsampled_vectors.tsv
LAST_MONTH=`date --date='-1 month' +%Y-%m`
INPUT=$SCRIPT_DIR/../out/$LAST_MONTH/vectors.tsv
OUTPUT=$SCRIPT_DIR/../out/$LAST_MONTH/downsampled_vectors.tsv

# The target number of points in a series
DOWNSAMPLE_TO=100

# Specifies where to find imported modules for python scripts
export PYTHONPATH=$SCRIPT_DIR/..

cat $INPUT | python3 $SCRIPT_DIR/downsample_tsv.py --downsample-to $DOWNSAMPLE_TO > $OUTPUT