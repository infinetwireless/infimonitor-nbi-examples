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
  --url "${URL_BASE}/hosts?${DELETED_AND_DEACTIVATED_PREDICATE}" \
  --quantity-of-parts 10 \
  > "${OUT_DIR}/hosts.tsv"
python3 "${SCRIPT_DIR}/../load_data/get_json_save_tsv.py" \
  --token ${TOKEN} \
  --url "${URL_BASE}/hosts/all/interfaces?${DELETED_AND_DEACTIVATED_PREDICATE}" \
  --quantity-of-parts 10 \
  > "${OUT_DIR}/hosts_interfaces.tsv"
python3 "${SCRIPT_DIR}/../load_data/get_json_save_tsv.py" \
  --token ${TOKEN} \
  --url "${URL_BASE}/hosts/all/interfaces/all/vectors?${DELETED_AND_DEACTIVATED_PREDICATE}" \
  --quantity-of-parts 10 \
  > "${OUT_DIR}/hosts_interfaces_vectors.tsv"
HOST_PARAMETERS="hostLabel,productFamily,sysSerialNumber,sysSoftwareVersion,sysModel,xgChannelWidth,xgUnitType"
python3 "${SCRIPT_DIR}/../load_data/get_json_save_tsv.py" \
  --token ${TOKEN} \
  --url "${URL_BASE}/hosts/all/parameters?parametersNames=${HOST_PARAMETERS}&${DELETED_AND_DEACTIVATED_PREDICATE}" \
  --quantity-of-parts 10 \
  > "${OUT_DIR}/hosts_parameters.tsv"
INTERFACES_PARAMETERS="ifDescr,ipAdEntAddr,rmBandwidth,rmFrequency"
python3 "${SCRIPT_DIR}/../load_data/get_json_save_tsv.py" \
  --token ${TOKEN} \
  --url "${URL_BASE}/interfaces/all/parameters?parametersNames=${INTERFACES_PARAMETERS}&${DELETED_AND_DEACTIVATED_PREDICATE}" \
  --quantity-of-parts 10 \
  > "${OUT_DIR}/interfaces_parameters.tsv"
VECTORS_PARAMETERS="xgCcFreqDl,xgCcFreqUl"
python3 "${SCRIPT_DIR}/../load_data/get_json_save_tsv.py" \
  --token ${TOKEN} \
  --url "${URL_BASE}/vectors/all/parameters?parametersNames=${VECTORS_PARAMETERS}&${DELETED_AND_DEACTIVATED_PREDICATE}" \
  --quantity-of-parts 10 \
  > "${OUT_DIR}/vectors_parameters.tsv"
