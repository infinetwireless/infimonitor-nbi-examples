REM All paths variables are related to directory where this script is localed
SET SCRIPT_DIR=%~dp0

SET REPORT_NAME=performance

REM A default date-time window of the loaded parameters history. Last full day i.e. yesterday by default,
python "%SCRIPT_DIR%\..\utilits\ms\wnd_date.py" --delta-days -1 --format "%%Y-%%m-%%dT00:00%%:z" > tmp
SET /P FROM=<tmp
DEL tmp
python "%SCRIPT_DIR%\..\utilits\ms\wnd_date.py"                 --format "%%Y-%%m-%%dT00:00%%:z" > tmp
SET /P TO=<tmp
DEL tmp
REM or can be specified manually as something like:
REM SET FROM=2017-06-01T00:00:00.000+05:00
REM SET TO=2017-07-01T00:00:00.000+05:00

REM A default output files directory. It is specified as a last full day i.e. yesterday like .../2018-07-04
python "%SCRIPT_DIR%\..\utilits\ms\wnd_date.py" --delta-days -1 --format "%%Y-%%m-%%d" > tmp
SET /P YESTERDAY=<tmp
DEL tmp
SET OUT_DIR=%SCRIPT_DIR%\..\..\out\%REPORT_NAME%\%YESTERDAY%
REM or can be specified manually:
REM SET OUT_DIR=%SCRIPT_DIR%\..\..\out\performance\2018-07-04


REM Specifies where to find imported modules for python scripts
SET "PYTHONPATH=%SCRIPT_DIR%\..\.."