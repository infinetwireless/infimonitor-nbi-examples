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
  --url "%URL_BASE%/links?%DELETED_AND_DEACTIVATED_PREDICATE%" ^
  --quantity-of-parts 10 ^
  > "%OUT_DIR%\links.tsv"
python "%SCRIPT_DIR%\..\load_data\get_json_save_tsv.py" ^
  --token %TOKEN% ^
  --url "%URL_BASE%/hosts/all/parameters?parametersNames=hostLabel&%DELETED_AND_DEACTIVATED_PREDICATE%" ^
  --quantity-of-parts 10 ^
  > "%OUT_DIR%\hosts_labels.tsv"
python "%SCRIPT_DIR%\..\load_data\get_json_save_tsv.py" ^
  --token %TOKEN% ^
  --url "%URL_BASE%/vectors/all/history?timestampFromIncl=%FROM%&timestampToExcl=%TO%" ^
  --quantity-of-parts 100 ^
  > "%OUT_DIR%\vectors_history.tsv"