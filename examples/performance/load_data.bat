@Echo off

REM All paths variables are related to directory where this script is localed
SET SCRIPT_DIR=%~dp0

REM Initialize common variables in a single place
CALL "%SCRIPT_DIR%\settings.bat"

REM You should specify your InfiMONITOR host
REM SET HOST=192.168.200.222
SET /P HOST="An InfiMONITOR host: "

REM You should copy an integrations API key value from the page https://%HOST%/settings.html#/settings/system
REM SET TOKEN=c7a67f60-002a-470f-b426-39ad3958dd6b
SET /P TOKEN="An integrations API key value from the page https://%HOST%/settings.html#/settings/system: "

IF NOT EXIST "%OUT_DIR%" MKDIR "%OUT_DIR%"

SET URL_BASE=https://%HOST%/api/nbi/v1.beta
SET "DELETED_AND_DEACTIVATED_PREDICATE=includeDeleted=false&includeDeactivated=false"
python "%SCRIPT_DIR%\..\load_data\get_json_save_tsv.py" ^
  --token %TOKEN% ^
  --url "%URL_BASE%/hosts?%DELETED_AND_DEACTIVATED_PREDICATE%" ^
  --quantity-of-parts 10 ^
  > "%OUT_DIR%\hosts.tsv"
python "%SCRIPT_DIR%\..\load_data\get_json_save_tsv.py" ^
  --token %TOKEN% ^
  --url "%URL_BASE%/hosts/all/interfaces?%DELETED_AND_DEACTIVATED_PREDICATE%" ^
  --quantity-of-parts 10 ^
  > "%OUT_DIR%\hosts_interfaces.tsv"
python "%SCRIPT_DIR%\..\load_data\get_json_save_tsv.py" ^
  --token %TOKEN% ^
  --url "%URL_BASE%/links?%DELETED_AND_DEACTIVATED_PREDICATE%" ^
  --quantity-of-parts 10 ^
  > "%OUT_DIR%\links.tsv"
SET "HOST_PARAMETERS=hostLabel,productFamily"
python "%SCRIPT_DIR%\..\load_data\get_json_save_tsv.py" ^
  --token %TOKEN% ^
  --url "%URL_BASE%/hosts/all/parameters?parametersNames=%HOST_PARAMETERS%&%DELETED_AND_DEACTIVATED_PREDICATE%" ^
  --quantity-of-parts 10 ^
  > "%OUT_DIR%\hosts_parameters.tsv"
SET "INTERFACES_PARAMETERS=ipAdEntAddr"
python "%SCRIPT_DIR%\..\load_data\get_json_save_tsv.py" ^
  --token %TOKEN% ^
  --url "%URL_BASE%/interfaces/all/parameters?parametersNames=%INTERFACES_PARAMETERS%&%DELETED_AND_DEACTIVATED_PREDICATE%" ^
  --quantity-of-parts 10 ^
  > "%OUT_DIR%\interfaces_parameters.tsv"
SET "VECTOR_TYPES_PREDICATE=vectorTypes=MINT,XG"
SET "VECTORS_CURRENT_PARAMETERS=vectorType"
python "%SCRIPT_DIR%\..\load_data\get_json_save_tsv.py" ^
  --token %TOKEN% ^
  --url "%URL_BASE%/vectors/all/parameters?%VECTOR_TYPES_PREDICATE%&parametersNames=%VECTORS_CURRENT_PARAMETERS%&%DELETED_AND_DEACTIVATED_PREDICATE%" ^
  --quantity-of-parts 10 ^
  > "%OUT_DIR%\vectors_parameters.tsv"
SET "VECTOR_HISTORY_PARAMETERS=currentLevel,retries,bitrate,xgCINR,xgABSRSSI,xgTotalCapacityTx"
SET "PERIOD_PREDICATE=timestampFromIncl=%FROM%&timestampToExcl=%TO%"
python "%SCRIPT_DIR%\..\load_data\get_json_save_tsv.py" ^
  --token %TOKEN% ^
  --url "%URL_BASE%/vectors/all/history?%VECTOR_TYPES_PREDICATE%&parametersNames=%VECTOR_HISTORY_PARAMETERS%&%PERIOD_PREDICATE%" ^
  --quantity-of-parts 100 ^
  > "%OUT_DIR%\vectors_history.tsv"
