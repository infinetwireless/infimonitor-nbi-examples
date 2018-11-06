@Echo off

REM All paths variables are related to directory where this script is localed
SET SCRIPT_DIR=%~dp0

REM Initialize common variables in a single place
CALL "%SCRIPT_DIR%\settings.bat"

python "%SCRIPT_DIR%\make_excel_report.py" ^
  "%OUT_DIR%\hosts_labels.tsv" "%OUT_DIR%\links.tsv" "%OUT_DIR%\downsampled_vectors_history.tsv" ^
  -o "%OUT_DIR%\%REPORT_NAME%.xlsx"
