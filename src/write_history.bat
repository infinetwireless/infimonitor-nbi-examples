set PYTHON=C:\Users\test\AppData\Local\Programs\Python\Python36-32\python.exe
set HOST=192.168.200.222
set PATH_PREFIX=/api/nbi/v1.beta
set URL_BASE=https://%HOST%%PATH_PREFIX%
set FROM=2017-06-01T00:00Z
set TO=2017-06-02T00:00Z
set TOKEN=bcab2bf0-39d6-4686-9ae8-31ea7495b674
set OUT_DIR=out

mkdir %OUT_DIR%
%PYTHON% get_json_save_tsv.py --token %TOKEN% --url %URL_BASE%/links --file %OUT_DIR%\links.tsv
%PYTHON% get_json_save_tsv.py --token %TOKEN% --url %URL_BASE%/hosts --file %OUT_DIR%\hosts.tsv
%PYTHON% get_json_save_tsv.py --token %TOKEN% --url "%URL_BASE%/vectors/all/history?timestampFromIncl=%FROM%&timestampToExcl=%TO%" --file %OUT_DIR%\vectors.tsv
pause