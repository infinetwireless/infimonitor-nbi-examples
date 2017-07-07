@Echo off

python ms\wnd_date.py --delta-months -1 --format %%Y-%%m > tmp
SET /P LAST_MONTH=<tmp
DEL tmp

SET INPUT=..\out\%LAST_MONTH%\vectors.tsv
SET OUTPUT=..\out\%LAST_MONTH%\downsampled_vectors.tsv
SET DOWNSAMPLE_TO=100

SET PYTHONPATH=..

python downsample_tsv.py --input %INPUT% --downsample-to %DOWNSAMPLE_TO% > %OUTPUT%