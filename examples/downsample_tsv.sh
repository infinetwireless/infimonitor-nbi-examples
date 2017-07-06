#!/bin/sh
INPUT=../out/vectors.tsv
OUTPUT=../out/downsampled_vectors.tsv
DOWNSAMPLE_TO=100
cat $INPUT | PYTHONPATH=.. python3 downsample_tsv.py --downsample-to $DOWNSAMPLE_TO > $OUTPUT