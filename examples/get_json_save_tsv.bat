@Echo off

REM All paths variables are related to directory where this script is localed
SET SCRIPT_DIR=%~dp0

REM Initialize common variables in a single place
CALL "%SCRIPT_DIR%\common_variables.bat"

REM You should specify your InfiMONITOR host
REM SET HOST=192.168.200.222
SET /P HOST="An InfiMONITOR host: "

REM You should copy an integrations API key value from the page https://%HOST%/settings.html#/settings/system
REM SET TOKEN=c7a67f60-002a-470f-b426-39ad3958dd6b
SET /P TOKEN="An integrations API key value from the page https://%HOST%/settings.html#/settings/system: "

REM A date-time window of the loaded parameters history. Last month by default,
SET FROM=%DEFAULT_FROM%
SET TO=%DEFAULT_TO%
REM or can be specified manually as something like:
REM SET FROM=2017-06-01T00:00:00.000+05:00
REM SET TO=2017-07-01T00:00:00.000+05:00

REM Output files path. By default specified as a last month like ..\out\2017-06
SET OUT_DIR=%DEFAULT_OUT_DIR%
REM or can be specified manually:
REM SET OUT_DIR=%SCRIPT_DIR%\..\out\2017-06

SET PATH_PREFIX=/api/nbi/v1.beta
SET URL_BASE=https://%HOST%%PATH_PREFIX%

IF NOT EXIST "%OUT_DIR%" MKDIR "%OUT_DIR%"
python "%SCRIPT_DIR%\get_json_save_tsv.py" ^
  --token %TOKEN% ^
  --url "%URL_BASE%/links?includeDeleted=true&includeDeactivated=true" ^
  --quantity-of-parts 10 ^
  > "%OUT_DIR%\links.tsv"
python "%SCRIPT_DIR%\get_json_save_tsv.py" ^
  --token %TOKEN% ^
  --url "%URL_BASE%/hosts/all/parameters?parametersNames=hostLabel&includeDeleted=true&includeDeactivated=true" ^
  --quantity-of-parts 10 ^
  > "%OUT_DIR%\hosts_labels.tsv"
python "%SCRIPT_DIR%\get_json_save_tsv.py" ^
  --token %TOKEN% ^
  --url "%URL_BASE%/vectors/all/history?timestampFromIncl=%FROM%&timestampToExcl=%TO%" ^
  --quantity-of-parts 100 ^
  > "%OUT_DIR%\vectors_history.tsv"