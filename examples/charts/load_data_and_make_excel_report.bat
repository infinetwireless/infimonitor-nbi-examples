@Echo off

REM All paths variables are related to directory where this script is localed
SET SCRIPT_DIR=%~dp0

CALL "%SCRIPT_DIR%\get_json_save_tsv.bat"
CALL "%SCRIPT_DIR%\downsample_tsv.bat"
CALL "%SCRIPT_DIR%\make_excel_report.bat"