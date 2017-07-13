@Echo off

REM All paths variables are related to directory where this script is localed
SET SCRIPT_DIR=%~p0

REM Input and output files. By default they are located in a last month named directory like ../out/2017-06
REM or can be specified manually as something like:
REM SET INPUT=..\out\2017-06\vectors.tsv
REM SET OUTPUT=..\out\2017-06\downsampled_vectors.tsv
python %SCRIPT_DIR%\ms\wnd_date.py --delta-months -1 --format %%Y-%%m > tmp
SET /P LAST_MONTH=<tmp
DEL tmp
SET INPUT=%SCRIPT_DIR%\..\out\%LAST_MONTH%\vectors.tsv
SET OUTPUT=%SCRIPT_DIR%\..\out\%LAST_MONTH%\downsampled_vectors.tsv

REM The target number of points in a series
SET DOWNSAMPLE_TO=100

REM Specifies where to find imported modules for python scripts
SET PYTHONPATH=%SCRIPT_DIR%\..

python %SCRIPT_DIR%\downsample_tsv.py --input %INPUT% --downsample-to %DOWNSAMPLE_TO% > %OUTPUT%