@Echo off

REM Input and output files. By default they are located in a last month named directory like ../out/2017-06
REM or can be specified manually as something like:
REM SET INPUT=..\out\2017-06\vectors.tsv
REM SET OUTPUT=..\out\2017-06\downsampled_vectors.tsv
python ms\wnd_date.py --delta-months -1 --format %%Y-%%m > tmp
SET /P LAST_MONTH=<tmp
DEL tmp
SET INPUT=..\out\%LAST_MONTH%\vectors.tsv
SET OUTPUT=..\out\%LAST_MONTH%\downsampled_vectors.tsv

REM The target number of points in a series
SET DOWNSAMPLE_TO=100

REM Specifies where to find imported libraries for python scripts
SET PYTHONPATH=..

python downsample_tsv.py --input %INPUT% --downsample-to %DOWNSAMPLE_TO% > %OUTPUT%