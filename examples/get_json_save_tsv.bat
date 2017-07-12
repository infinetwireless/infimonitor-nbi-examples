@Echo off

REM You should specify your InfiMONITOR host
REM SET HOST=192.168.200.222
SET /P HOST="An InfiMONITOR host: "

REM You should copy an integrations API key value from the page https://%HOST%/settings.html#/settings/system
REM SET TOKEN=c7a67f60-002a-470f-b426-39ad3958dd6b
SET /P TOKEN="An integrations API key value from the page https://%HOST%/settings.html#/settings/system: "

REM A date-time window of the loaded parameters history. Last month by default,
REM or can be specified manually as something like:
REM SET FROM=2017-06-01T00:00:00.000+05:00Z
REM SET TO=2017-07-01T00:00:00.000+05:00Z
python ms\wnd_date.py --delta-months -1 --format %%Y-%%m-01T00:00%%:z > tmp
SET /P FROM=<tmp
DEL tmp
python ms\wnd_date.py                   --format %%Y-%%m-01T00:00%%:z > tmp
SET /P TO=<tmp
DEL tmp

REM Output files path. By default specified as a last month like ..\out\2017-06
python ms\wnd_date.py --delta-months -1 --format %%Y-%%m > tmp
SET /P LAST_MONTH=<tmp
DEL tmp
SET OUT_DIR=..\out\%LAST_MONTH%

SET PATH_PREFIX=/api/nbi/v1.beta
SET URL_BASE=https://%HOST%%PATH_PREFIX%

IF NOT EXIST %OUT_DIR% MKDIR %OUT_DIR%
python get_json_save_tsv.py --token %TOKEN% --url %URL_BASE%/links > %OUT_DIR%\links.tsv
python get_json_save_tsv.py --token %TOKEN% --url %URL_BASE%/hosts > %OUT_DIR%\hosts.tsv
python get_json_save_tsv.py --token %TOKEN% ^
--url "%URL_BASE%/vectors/all/history?timestampFromIncl=%FROM%&timestampToExcl=%TO%" > %OUT_DIR%\vectors.tsv
