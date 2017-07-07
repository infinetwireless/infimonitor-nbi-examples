@Echo off

REM Input and output files directory. By default it is last month named directory like ..\out\2017-06
REM It can be specified manually as something like:
REM DIR=..\out\2017-06
python ms\wnd_date.py --delta-months -1 --format %%Y-%%m > tmp
SET /P LAST_MONTH=<tmp
DEL tmp
SET DIR=..\out\%LAST_MONTH%

python make_excel_report.py "%DIR%\hosts.tsv" "%DIR%\links.tsv" "%DIR%\downsampled_vectors.tsv" -o %DIR%\report.xlsx
