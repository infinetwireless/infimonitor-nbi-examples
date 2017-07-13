#!/bin/sh

# All paths variables are related to directory where this script is localed
SCRIPT_DIR=$(dirname $(realpath $0))

# You should specify your InfiMONITOR host
# HOST=192.168.200.222
read -p "An InfiMONITOR host: " HOST

# You should copy an integrations API key value from the page https://$HOST/settings.html#/settings/system
# TOKEN=c7a67f60-002a-470f-b426-39ad3958dd6b
read -p "An integrations API key value from the page https://$HOST/settings.html#/settings/system: " TOKEN

# A date-time window of the loaded parameters history. Last month by default,
# or can be specified manually as something like:
# FROM=2017-06-01T00:00:00.000+05:00Z
# TO=2017-07-01T00:00:00.000+05:00Z
FROM=`date --date='-1 month' +%Y-%m-01T00:00%:z`
TO=`date                   +%Y-%m-01T00:00%:z`

# Output files path. By default specified as a last month like ../out/2017-06
LAST_MONTH=`date --date='-1 month' +%Y-%m`
OUT_DIR=$SCRIPT_DIR/../out/$LAST_MONTH

PATH_PREFIX=/api/nbi/v1.beta
URL_BASE=https://$HOST$PATH_PREFIX

mkdir -p $OUT_DIR
python3 $SCRIPT_DIR/get_json_save_tsv.py --token $TOKEN \
 --url "$URL_BASE/vectors/all/history?timestampFromIncl=$FROM&timestampToExcl=$TO" \
 --page-size $((1024*16)) > $OUT_DIR/vectors.tsv
python3 $SCRIPT_DIR/get_json_save_tsv.py --token $TOKEN --url "$URL_BASE/links" > $OUT_DIR/links.tsv
python3 $SCRIPT_DIR/get_json_save_tsv.py --token $TOKEN --url "$URL_BASE/hosts" > $OUT_DIR/hosts.tsv
