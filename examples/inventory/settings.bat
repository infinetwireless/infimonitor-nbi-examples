REM All paths variables are related to directory where this script is localed
SET SCRIPT_DIR=%~dp0

SET REPORT_NAME=inventory

REM An output files directory. It is specified as a current date like ...\2018-06-27
python "%SCRIPT_DIR%\..\utilits\ms\wnd_date.py" --format "%%Y-%%m-%%d" > tmp
SET /P TODAY=<tmp
DEL tmp
SET OUT_DIR=%SCRIPT_DIR%\..\..\out\%REPORT_NAME%\%TODAY%
REM or can be specified manually:
REM SET OUT_DIR=%SCRIPT_DIR%\..\..\out\inventory\2017-06-27


REM Specifies where to find imported modules for python scripts
SET "PYTHONPATH=%SCRIPT_DIR%\..\.."