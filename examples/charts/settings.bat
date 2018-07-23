REM All paths variables are related to directory where this script is localed
SET SCRIPT_DIR=%~dp0

SET REPORT_NAME=charts

REM A default date-time window of the loaded parameters history. Last month by default,
python "%SCRIPT_DIR%\..\utilits\ms\wnd_date.py" --delta-months -1 --format "%%Y-%%m-01T00:00%%:z" > tmp
SET /P FROM=<tmp
DEL tmp
python "%SCRIPT_DIR%\..\utilits\ms\wnd_date.py"                   --format "%%Y-%%m-01T00:00%%:z" > tmp
SET /P TO=<tmp
DEL tmp
REM or can be specified manually as something like:
REM SET FROM=2017-06-01T00:00:00.000+05:00
REM SET TO=2017-07-01T00:00:00.000+05:00

REM A default output files directory. It is specified as a last month like ...\2017-06
python "%SCRIPT_DIR%\..\utilits\ms\wnd_date.py" --delta-months -1 --format "%%Y-%%m" > tmp
SET /P LAST_MONTH=<tmp
DEL tmp
SET OUT_DIR=%SCRIPT_DIR%\..\..\out\%REPORT_NAME%\%LAST_MONTH%
REM or can be specified manually:
REM SET OUT_DIR=%SCRIPT_DIR%\..\..\out\charts\2017-06

REM The target number of points in a series after downsampling
SET DOWNSAMPLE_TO=100

REM Specifies where to find imported modules for python scripts
SET "PYTHONPATH=%SCRIPT_DIR%\..\.."