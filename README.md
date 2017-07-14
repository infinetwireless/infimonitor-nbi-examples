# InfiMONITOR Northbound Interface usage examples
Northbound Interface is a programming interface for integration with the higher-level system.

InfiMONITOR NBI is a RESTfull API. A RESTful API is an application program interface that uses HTTP requests
 to GET, PUT, POST and DELETE data.
 
Swagger 2 used to produce actual REST API documentation at https://{INFIMONITOR_HOST}/api/nbi/swagger-ui.html

## Install
Python 3 with PIP are required.

    Windows:
        Download from www.python.org
        Install and add to PATH variable (checkbox in the installation wizard)
    
    Ubuntu:
        sudo apt-get install python3 python3-pip
    
    CentOS:
        sudo yum install python34 python34-pip
    
    CentOS SCL:
        sudo yum install rh-python35 rh-python35-pip
        
    ...

Packages from PyPI used by examples scripts are also required.

    Windows:
        pip install --requirement requirements.txt
    
    Linux:
        sudo pip3 install --requirement requirements.txt

## Description
Script **get_json_save_tsv.py** allows to get tabular data from InfiMONITOR NBI and store it as a tab separated values file.

    usage: get_json_save_tsv.py [-h] [--url URL] --token TOKEN [--file FILE] [--page-size PAGE_SIZE]
    optional arguments:
      -h, --help            show this help message and exit
      --url URL             REST API entry point URL
      --token TOKEN         REST API token
      --file FILE           Path to the tsv file otherwise stdout will be used
      --page-size PAGE_SIZE Number of JSON objects in a single HTTP response

Scripts **get_json_save_tsv.bat** or **get_json_save_tsv.sh** 
uses **get_json_save_tsv.py** to load hosts, links and parameters values history for a last month.

Script **downsample_tsv.py** allows to downsample parameters values history to given number of points. 
It expects that input is a TSV file with five columns: 
nmsObjectUuid, parameterName, timestamp, index, value 
and that data in this file is sorted ascending by first three columns.
To downsample data with try to retain its visual characteristics used 
Steinarsson’s Largest Triangle Three Buckets algorithm and slightly modified copy of its implementation 
from [javiljoen/lttb.py](https://github.com/javiljoen/lttb.py)

    usage: downsample_tsv.py [-h] [--downsample-to DOWNSAMPLE_TO] [--input INPUT] [--output OUTPUT]
    optional arguments:
      -h, --help            show this help message and exit
      --downsample-to DOWNSAMPLE_TO
                            desired number of points per series
      --input INPUT         input tsv file otherwise stdin will be used
      --output OUTPUT       output tsv file otherwise stdout will be used

Scripts **downsample_tsv.bat** or **downsample_tsv.sh** uses **downsample_tsv.py** to 
downsample parameters values history found in directory corresponding to a last month.

Script **make_excel_report.py** generates MS Excel 
report about parameters values history associated with links using three TSV files describing 
hosts, links and parameters values history. It expects that parameters values history file is 
sorted ascending by first three columns. 

    usage: make_excel_report.py [-h] [-q] [-o O] hosts-tsv links-tsv history-tsv
    positional arguments:
      hosts-tsv    Path to tsv formatted file that containing columns: (uuid, name)
      links-tsv    Path to tsv formatted file that containing columns: (id, uuid,
                   exists, activated, hostAUuid, hostBUuid, ifaceAUuid,
                   ifaceBUuid, vectorAUuid, vectorBUuid)
      history-tsv  Path to tsv formatted file that containing columns:
                   (nmsObjectUuid, parameterName, timestamp, index, value)
    optional arguments:
      -h, --help   show this help message and exit
      -q           quiet output
      -o O         create output xlsx in a specified output file. By defaults
                   output file will be created in the folder from which the script
                   was launched.

Script **make_excel_report.bat** uses **make_excel_report.py** to generate MS Excel report
 using hosts, links and parameters values history found in directory corresponding to a last month.

Script **load_data_and_make_excel_report.bat** - all in one to get data from InfiMONITOR NBI, 
downsample it and to generate a MS Excel report for a last month.

Default values such as an output directory or a report dates window corresponding to a last month 
are specified in files **common_variables.bat** or **common_variables.sh**