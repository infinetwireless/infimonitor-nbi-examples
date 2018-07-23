@Echo off

REM All paths variables are related to directory where this script is localed
SET SCRIPT_DIR=%~dp0

REM Initialize common variables in a single place
CALL "%SCRIPT_DIR%\settings.bat"

python "%SCRIPT_DIR%\make_hosts_performance_xlsx_report.py" ^
  --data-dir "%OUT_DIR%" ^
  --report-file "%OUT_DIR%\hosts_%REPORT_NAME%.xlsx"
