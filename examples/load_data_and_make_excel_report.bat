@Echo off

REM All paths variables are related to directory where this script is localed
SET SCRIPT_DIR=%~p0

call %SCRIPT_DIR%\get_json_save_tsv.bat
call %SCRIPT_DIR%\downsample_tsv.bat
call %SCRIPT_DIR%\make_excel_report.bat