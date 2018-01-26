@Echo off

REM All paths variables are related to directory where this script is localed
SET SCRIPT_DIR=%~dp0

REM Initialize common variables in a single place
CALL "%SCRIPT_DIR%\common_variables.bat"

REM Input and output files. By default they are located in a last month named directory like ../out/2017-06
SET INPUT=%DEFAULT_OUT_DIR%\vectors_history.tsv
SET OUTPUT=%DEFAULT_OUT_DIR%\downsampled_vectors_history.tsv
REM or can be specified manually as something like:
REM SET INPUT=%SCRIPT_DIR%\..\out\2017-06\vectors_history.tsv
REM SET OUTPUT=%SCRIPT_DIR%\..\out\2017-06\downsampled_vectors_history.tsv

REM The target number of points in a series
SET DOWNSAMPLE_TO=100

REM Specifies where to find imported modules for python scripts
SET "PYTHONPATH=%SCRIPT_DIR%\.."

python "%SCRIPT_DIR%\downsample_tsv.py" --input "%INPUT%" --downsample-to %DOWNSAMPLE_TO% > "%OUTPUT%"