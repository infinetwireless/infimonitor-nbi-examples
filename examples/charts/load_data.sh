#! /usr/bin/env bash
set -euo pipefail

# All paths variables are related to directory where this script is localed
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Initialize script variables in a single place
. "${SCRIPT_DIR}/settings.sh"

# You should specify your InfiMONITOR host
# HOST=192.168.200.222
read -p "An InfiMONITOR host: " HOST

# You should copy an integrations API key value from the page https://${HOST}/settings.html#/settings/system
# TOKEN=c7a67f60-002a-470f-b426-39ad3958dd6b
read -p "An integrations API key value from the page https://${HOST}/settings.html#/settings/system: " TOKEN

mkdir -p "${OUT_DIR}"

URL_BASE=https://${HOST}/api/nbi/v1.beta
DELETED_AND_DEACTIVATED_PREDICATE="includeDeleted=false&includeDeactivated=false"
python3 "${SCRIPT_DIR}/../load_data/get_json_save_tsv.py" \
  --token ${TOKEN} \
  --url "${URL_BASE}/links?${DELETED_AND_DEACTIVATED_PREDICATE}" \
  --quantity-of-parts 10 \
  > "${OUT_DIR}/links.tsv"
python3 "${SCRIPT_DIR}/../load_data/get_json_save_tsv.py" \
  --token ${TOKEN} \
  --url "${URL_BASE}/hosts/all/parameters?parametersNames=hostLabel&${DELETED_AND_DEACTIVATED_PREDICATE}" \
  --quantity-of-parts 10 \
  > "${OUT_DIR}/hosts_labels.tsv"
python3 "${SCRIPT_DIR}/../load_data/get_json_save_tsv.py" \
  --token ${TOKEN} \
  --url "${URL_BASE}/vectors/all/history?timestampFromIncl=${FROM}&timestampToExcl=${TO}" \
  --quantity-of-parts 100 \
  > "${OUT_DIR}/vectors_history.tsv"
