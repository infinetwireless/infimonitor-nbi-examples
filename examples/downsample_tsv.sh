#!/bin/sh
LAST_MONTH=`date --date='-1 month' +%Y-%m`
INPUT=../out/$LAST_MONTH/vectors.tsv
OUTPUT=../out/$LAST_MONTH/downsampled_vectors.tsv
DOWNSAMPLE_TO=100

export PYTHONPATH=..

cat $INPUT | python3 downsample_tsv.py --downsample-to $DOWNSAMPLE_TO > $OUTPUT