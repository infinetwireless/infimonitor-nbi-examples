#!/bin/sh

# Input and output files. By default they are located in a last month named directory like ../out/2017-06
# They can be specified manually as something like:
# INPUT=../out/2017-06/vectors.tsv
# OUTPUT=../out/2017-06/downsampled_vectors.tsv
LAST_MONTH=`date --date='-1 month' +%Y-%m`
INPUT=../out/$LAST_MONTH/vectors.tsv
OUTPUT=../out/$LAST_MONTH/downsampled_vectors.tsv

# The target number of points in a series
DOWNSAMPLE_TO=100

# Specifies where to find imported libraries for python scripts
export PYTHONPATH=..

cat $INPUT | python3 downsample_tsv.py --downsample-to $DOWNSAMPLE_TO > $OUTPUT