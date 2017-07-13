@Echo off

REM All paths variables are related to directory where this script is localed
SET SCRIPT_DIR=%~p0

REM Input and output files directory. By default it is last month named directory like ..\out\2017-06
REM It can be specified manually as something like:
REM DIR=..\out\2017-06
python %SCRIPT_DIR%\ms\wnd_date.py --delta-months -1 --format %%Y-%%m > tmp
SET /P LAST_MONTH=<tmp
DEL tmp
SET DIR=%SCRIPT_DIR%\..\out\%LAST_MONTH%

REM Specifies where to find imported modules for python scripts
SET PYTHONPATH=%SCRIPT_DIR%\..

python %SCRIPT_DIR%\make_excel_report.py "%DIR%\hosts.tsv" "%DIR%\links.tsv" "%DIR%\downsampled_vectors.tsv" -o %DIR%\report.xlsx
