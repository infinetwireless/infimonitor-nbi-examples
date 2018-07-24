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
### Loading data
Script **examples/load_data/get_json_save_tsv.py** allows to get tabular data from InfiMONITOR NBI 
and store it as a tab separated values file. This script is reused to load data for scripts what build reports 
(charts, inventory and performance).

    usage: get_json_save_tsv.py [-h] [--url URL] --token TOKEN [--file FILE] [--page-size PAGE_SIZE] [--quantity-of-parts PARTS]
    optional arguments:
      -h, --help                 show this help message and exit
      --url URL                  REST API entry point URL
      --token TOKEN              REST API token
      --file FILE                Path to the tsv file otherwise stdout will be used
      --page-size PAGE_SIZE      Number of JSON objects in a single HTTP response 
                                 (can be very slow on a large amount of data, use --quantity-of-parts instead)
      --quantity-of-parts PARTS  Number of parts on which the uploaded data is divided

*See more about available REST API entry points at https://{INFIMONITOR_HOST}/api/nbi/swagger-ui.html*   

### Charts report
The charts report building consists of three stages: loading data, downsampling series and 
making the MS Excel file.

#### Loading data
Scripts **examples/charts/load_data.bat** or **examples/charts/load_data.sh** uses 
**examples/load_data/get_json_save_tsv.py** to load hosts, links and parameters values history 
for a specified dates range. The downloaded data is placed in the specified directory, 
by default this is **out/charts/{last month}**.

#### Downsampling series
Script **examples/charts/downsample_tsv.py** allows to downsample parameters values history 
to a given number of points. This script expects that the input is a TSV file with five columns: 
**nmsObjectUuid, parameterName, timestamp, index, value** 
and that its data is grouped by **nmsObjectUuid, parameterName** and sorted ascending by **timestamp** column.
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

Scripts **examples/charts/downsample_tsv.bat** or **examples/charts/downsample_tsv.sh** uses 
**examples/charts/downsample_tsv.py** to downsample parameters values history tsv file located in a directory 
where it was downloaded. 

#### Making the MS Excel file
The script described below demonstrates work with Excel through COM interface. Excel COM interface 
provides the most complete set of features for generating Excel files, but it is slow and works only in the 
appropriate environment.

Script **examples/charts/make_excel_report.py** generates MS Excel report about parameters values history 
associated with links. The report consists of two sheets: the first sheet shows the graphs of the history 
of the values of links parameters, the second sheet holds data necessary for the construction of these graphs. 
The script expects that parameters values history file data is grouped by **nmsObjectUuid, parameterName** and 
sorted ascending by **timestamp** column.

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

Script **examples/charts/make_excel_report.bat** uses **examples/charts/make_excel_report.py** to generate 
MS Excel report using tsv files with hosts, links and downsampled parameters values history located in a 
directory where they was downloaded and downsampled.

#### Three in one script 
Script **examples/charts/load_data_and_make_excel_report.bat** - all in one to get data from InfiMONITOR NBI, 
downsample history series and to make the MS Excel file.

#### Settings
Scripts **examples/charts/settings.bat** or **examples/charts/settings.sh** are called from other scripts and 
allow to set following report parameters:
- A date-time window of the loaded parameters history
- An output files directory
- The target number of points in a series after downsampling

Scripts **examples/charts/load_data.bat** or **examples/charts/load_data.sh** ask the user to enter 
the InfiMONITOR host and the integrations API key, these parameters can be set in the scripts themselves. 

### Inventory report
The inventory report building consists of two stages: loading data and making the xlsx file.

#### Loading data
Scripts **examples/inventory/load_data.bat** or **examples/inventory/load_data.sh** uses 
**examples/load_data/get_json_save_tsv.py** to load hosts, interfaces, vectors and its parameters. 
The downloaded data is placed in the specified directory, by default this is **out/inventory/{today}**.

#### Making the xlsx file
Script **examples/inventory/make_xlsx_report.py** generates a xlsx report containing a list of hosts 
observed by the InfiMONITOR and their parameters. 

    usage: make_xlsx_report.py [-h] --data-dir DATA_DIR [--report-file REPORT_FILE]
    optional arguments:
      -h, --help                 show this help message and exit
      --data-dir DATA_DIR        directory with report data files: hosts.tsv, hosts_interfaces.tsv, 
                                 hosts_interfaces_vectors.tsv, hosts_parameters.tsv, interfaces_parameters.tsv, 
                                 vectors_parameters.tsv
      --report-file REPORT_FILE  path to the xlsx report file

Script **examples/inventory/make_excel_report.bat** or **examples/inventory/make_excel_report.sh** uses 
**examples/inventory/make_excel_report.py** to generate report as a xlsx file using tsv files with hosts, 
interfaces, vectors and its parameters located in a directory where they was downloaded.
      
#### Settings
Scripts **examples/inventory/settings.bat** or **examples/inventory/settings.sh** are called from 
other scripts and allow to set the output files directory for the report. 

Scripts **examples/inventory/load_data.bat** or **examples/inventory/load_data.sh** ask the user to enter 
the InfiMONITOR host and the integrations API key, these parameters can be set in the scripts themselves. 

### Performance report
The performance report building consists of two stages: loading data and making the xlsx file.

#### Loading data
Scripts **examples/performance/load_data.bat** or **examples/performance/load_data.sh** uses 
**examples/load_data/get_json_save_tsv.py** to load hosts, interfaces, links, hosts parameters, 
interfaces parameters, vectors (half link) parameters and vectors parameters values history. 
The downloaded data is placed in the specified directory, by default this is **out/performance/{yesterday}**.

#### Making the xlsx file
Script **examples/performance/make_xlsx_report.py** generates a xlsx report about links performance parameters. 
The report consists of two sheets: the first sheet shows the performance parameters of R5000 links, the second 
sheet holds shows the performance of XG links.

    usage: make_xlsx_report.py [-h] --data-dir DATA_DIR [--report-file REPORT_FILE]
    optional arguments:
      -h, --help                 show this help message and exit
      --data-dir DATA_DIR        directory with report data files: hosts.tsv, hosts_interfaces.tsv, 
                                 links.tsv, hosts_parameters.tsv,interfaces_parameters.tsv, 
                                 vectors_parameters.tsv, vectors_history.tsv
      --report-file REPORT_FILE  path to the xlsx report file

Script **examples/performance/make_excel_report.bat** or **examples/performance/make_excel_report.sh** uses 
**examples/performance/make_excel_report.py** to generate report as a xlsx file using tsv files with hosts, 
interfaces, vectors, links, its parameters and vectors history located in a directory where they was downloaded.

#### Settings
Scripts **examples/performance/settings.bat** or **examples/performance/settings.sh** are called from 
other scripts and allow to set following report parameters:
- A date-time window of the loaded parameters history
- An output files directory

Scripts **examples/performance/load_data.bat** or **examples/performance/load_data.sh** ask the user to enter 
the InfiMONITOR host and the integrations API key, these parameters can be set in the scripts themselves. 
