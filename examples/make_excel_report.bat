@Echo off

REM All paths variables are related to directory where this script is localed
SET SCRIPT_DIR=%~p0

REM Initialize common variables in a single place
CALL %SCRIPT_DIR%\common_variables.bat

REM Input and output files directory. By default it is last month named directory like ..\out\2017-06
SET OUT_DIR=%DEFAULT_OUT_DIR%
REM Also it can be specified manually as something like:
REM OUT_DIR=%SCRIPT_DIR%\..\out\2017-06

REM Specifies where to find imported modules for python scripts
SET PYTHONPATH=%SCRIPT_DIR%\..

python %SCRIPT_DIR%\make_excel_report.py ^
  "%OUT_DIR%\hosts.tsv" "%OUT_DIR%\links.tsv" "%OUT_DIR%\downsampled_vectors.tsv" -o %OUT_DIR%\report.xlsx
