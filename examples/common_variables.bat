REM All paths variables are related to directory where this script is localed
SET SCRIPT_DIR=%~dp0

REM A default date-time window of the loaded parameters history. Last month by default,
python "%SCRIPT_DIR%\ms\wnd_date.py" --delta-months -1 --format %%Y-%%m-01T00:00%%:z > tmp
SET /P DEFAULT_FROM=<tmp
DEL tmp
python "%SCRIPT_DIR%\ms\wnd_date.py"                   --format %%Y-%%m-01T00:00%%:z > tmp
SET /P DEFAULT_TO=<tmp
DEL tmp
REM or can be specified manually as something like:
REM SET DEFAULT_FROM=2017-06-01T00:00:00.000+05:00
REM SET DEFAULT_TO=2017-07-01T00:00:00.000+05:00

REM A default output files directory. It is specified as a last month like ..\out\2017-06
python "%SCRIPT_DIR%\ms\wnd_date.py" --delta-months -1 --format %%Y-%%m > tmp
SET /P LAST_MONTH=<tmp
DEL tmp
SET DEFAULT_OUT_DIR=%SCRIPT_DIR%\..\out\%LAST_MONTH%
REM or can be specified manually:
REM SET DEFAULT_OUT_DIR=%SCRIPT_DIR%\..\out\2017-06