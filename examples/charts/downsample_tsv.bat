@Echo off

REM All paths variables are related to directory where this script is localed
SET SCRIPT_DIR=%~dp0

REM Initialize common variables in a single place
CALL "%SCRIPT_DIR%\settings.bat"

python "%SCRIPT_DIR%\downsample_tsv.py" ^
  --input "%OUT_DIR%\vectors_history.tsv" ^
  --downsample-to %DOWNSAMPLE_TO% ^
  --estimate-progress ^
  > "%OUT_DIR%\downsampled_vectors_history.tsv"