#!/bin/sh
HOST=localhost
PATH_PREFIX=/api/nbi/v1.beta
URL_BASE=https://$HOST$PATH_PREFIX
FROM=2017-01-01T00:00Z
TO=2017-06-01T00:00Z
TOKEN=aaa
OUT_DIR=../out

mkdir -p $OUT_DIR
python3 get_json_save_tsv.py --token $TOKEN --url "$URL_BASE/vectors/all/history?timestampFromIncl=$FROM&timestampToExcl=$TO" > ./$OUT_DIR/vectors.tsv
python3 get_json_save_tsv.py --token $TOKEN --url "$URL_BASE/links" > ./$OUT_DIR/links.tsv
python3 get_json_save_tsv.py --token $TOKEN --url "$URL_BASE/hosts" > ./$OUT_DIR/hosts.tsv
