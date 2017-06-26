"""Generate a small excel report

 This module is generate .xlsx file with graphs by data from .tsv files

"""

import argparse
import re
import os
import sys
import csv
from datetime import datetime
import win32com.client

# Import dynamically generated com interface modules
# for Microsoft Office Object Library and Microsoft Excel Object Library
import MSO, MSE

quiet = False
outff = open("out.txt", 'w')

def message(str):
    global quiet
    if not quiet:
        outff.write('{}\n'.format(str))
        print(str)
        
def merge(l1, l2):
    res = []
    for i in l1 + l2:
        if i not in res:
            res.append(i)
    return res

def convertTimestamp(str):
    # Parse ISO 8601 timestamp
    res = str.replace('Z','+00:00')
    res = re.sub('([^.]+)(\.\d+)?([+-]\d\d):(\d\d)', '\g<1>\g<3>\g<4>', res)
    parsed = datetime.strptime(res, "%Y-%m-%dT%H:%M:%S%z").astimezone()
    return parsed.strftime('%Y.%m.%d %H:%M:%S')

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-q', action='store_true', help='quiet output')

    parser.add_argument('-o', default='report.xlsx',
                        help='create output xlsx in a specified output file.\
                        By defaults output file will be created in the folder \
                        from which the script was launched.')

    parser.add_argument('hosts-tsv', nargs=1,
                        help='Path to tsv formatted file that containing columns: \
                              (uuid, name)')

    parser.add_argument('links-tsv', nargs=1,
                        help='Path to tsv formatted file that containing columns: \
                              (id, uuid, exists, activated, hostAUuid, hostBUuid, \
                              ifaceAUuid, ifaceBUuid, vectorAUuid, vectorBUuid)')

    parser.add_argument('history-tsv', nargs=1,
                        help='Path to tsv formatted file that containing columns: \
                              (nmsObjectUuid, parameterName, timestamp, index, value)')
    
    args = vars(parser.parse_args())
    
    global quiet
    quiet = args['q']
    
    outputName = os.path.abspath(args['o'])
    hostsTSV = os.path.abspath(args['hosts-tsv'][0])
    linksTSV = os.path.abspath(args['links-tsv'][0])
    historyTSV = os.path.abspath(args['history-tsv'][0])

    reporter = Reporter()
    reporter.makeReport(outputName, hostsTSV, linksTSV, historyTSV)
    
    outff.close()

class Table:
    startCol = 0
    startRow = 0
    cols = 0
    rows = 0
    
    def __init__(self, col, row, cols, rows):
        self.startCol = col
        self.startRow = row
        self.cols = cols
        self.rows = rows
    
    def getColRange(self, ws, colNum):
        col = self.startCol + colNum - 1
        row1 = self.startRow
        row2 = self.startRow + self.rows - 1
        return ws.Range(ws.Cells(row1, col), ws.Cells(row2, col))
    
    def getRange(self, ws):
        col1 = self.startCol
        col2 = self.startCol + self.cols - 1
        row1 = self.startRow
        row2 = self.startRow + self.rows - 1
        return ws.Range(ws.Cells(row1, col1), ws.Cells(row2, col2))

class DataStore:
    lastColNum = 1
    dataSheet = None
    lastTable = None
    
    def __init__(self, sheet):
        self.dataSheet = sheet

    def allocateTable(self, cols):
        colNum = self.lastColNum
        rowNum = 1
        self.lastColNum += cols
        return Table(colNum, rowNum, cols, 0)

    def write(self, table, rows):
        addTable = Table(table.startCol, table.rows + 1, table.cols, len(rows))
        addRange = addTable.getRange(self.dataSheet)
        addRange.Value = rows
        table.rows += len(rows)

class Reader:
    csvReader = None
    csvHeader = None

    def __init__(self, file):
        self.csvReader = csv.reader(file, delimiter='\t', quoting=csv.QUOTE_NONE)
        self.csvHeader = next(self.csvReader)
            
    def __iter__(self):
        return self

    def __next__(self):
        arr = next(self.csvReader)
        row = dict(zip(self.csvHeader, arr))
        return row
    
class Reporter:
    GRAPH_HEIGHT = 300
    GRAPH_WIDTH = 500
    LABEL_DEPTH = 50

    xl = wb = reportSheet = dataSheet = None

    def __init__(self):
        self.xl = win32com.client.gencache.EnsureDispatch('Excel.Application')
        
    def makeReport(self, resultFile, hostsFile, linksFile, historyFile):
        self.wb = self.xl.Workbooks.Add()
		while self.wb.Worksheets.Count <= 2:
            self.wb.Worksheets.Add()
        self.reportSheet = self.wb.Worksheets(1)
        self.dataSheet = self.wb.Worksheets(2)
        self.reportSheet.Name = 'Report'
        self.dataSheet.Name = 'Data'
        
        hosts, links, metadata = self.prepareData(hostsFile, linksFile, historyFile)
        self.drawGraphs(hosts, links, metadata)
        
        self.wb.SaveAs(resultFile)
        self.wb.Close(False)
        self.xl.Application.Quit()
        
        message('Finish, result file is {}'.format(resultFile))

    def prepareData(self, hostsFile, linksFile, historyFile):
        hosts = {}
        links = {}
        history = {}
        dataStore = DataStore(self.dataSheet)      
        
        # Handle hosts rows
        message('Reading {}'.format(hostsFile))
        with open(hostsFile) as f:
            for row in Reader(f):
                hosts[row['uuid']] = row['name']
                

        # Handle links rows
        message('Reading {}'.format(linksFile))
        with open(linksFile) as f:
            for row in Reader(f):
                links[row['uuid']] = row

                
        # Handle history rows
        message('Reading {}'.format(historyFile))

        bufferedRecordsMax = 1024
        bufferedRecordsCount = 0
        bufferedRecords = {}
        with open(historyFile) as f:
            for row in Reader(f):
                uuid = row['nmsObjectUuid']
                paramName = row['parameterName']
                paramIndex = row['index']
                value = row['value'] if row['value'] != 'null' else ''
                timestamp = convertTimestamp(row['timestamp'])
                
                data = [timestamp, value]

                if uuid not in history:
                    history[uuid] = {}

                if paramName not in history[uuid]:
                    history[uuid][paramName] = {}

                if paramIndex not in history[uuid][paramName]:
                    history[uuid][paramName][paramIndex] = dataStore.allocateTable(len(data))
                
                if (uuid, paramName, paramIndex) not in bufferedRecords:
                    bufferedRecords[(uuid, paramName, paramIndex)] = []
                    
                bufferedRecords[(uuid, paramName, paramIndex)].append(data)
                bufferedRecordsCount += 1
                
                if bufferedRecordsCount > bufferedRecordsMax:
                    length, key = max([(len(val), key) for key, val in bufferedRecords.items()])
                    message('cache length {}'.format(length))
                    dataStore.write(history[key[0]][key[1]][key[2]], bufferedRecords[key])
                    bufferedRecords.pop(key, None)
                    bufferedRecordsCount -= length
            
            for key, val in bufferedRecords.items():
                dataStore.write(history[key[0]][key[1]][key[2]], val)

            bufferedRecords = {}
            bufferedRecordsCount = 0
            
        return hosts, links, history
    
    def drawGraphs(self, hosts, links, history):
        rs = self.reportSheet
        ds = self.dataSheet
        
        def drawLabel(name, text, upward, left, top, width , height):
            shp = rs.Shapes.AddShape(MSO.constants.msoShapeRectangle, left, top, width, height)
            shp.Name = name
            shp.TextFrame.Orientation = MSO.constants.msoTextOrientationUpward if upward else MSO.constants.msoTextOrientationHorizontal
            shp.TextFrame.Characters().Text = text
        
        def drawGraph(name, title, data, left, top, width , height):
            cht = rs.ChartObjects().Add(Left=left, Width=width, Top=top, Height=height)
            cht.Name = name
            cht.Chart.ChartType = MSE.constants.xlLineStacked
            cht.Chart.HasTitle = True
            cht.Chart.ChartTitle.Text = title
            cht.Chart.ChartTitle.Font.Size = 10
            
            for i, d in enumerate(data, start=1):
                cht.Chart.SeriesCollection().NewSeries()
                cht.Chart.SeriesCollection(i).Name = d['lineName']
                cht.Chart.SeriesCollection(i).XValues = d['XRange']
                cht.Chart.SeriesCollection(i).Values = d['YRange']
        
        allParameters = []
        linksWithParameters = []
        for _, l in links.items():
            vectorAMetadata = history.get(l['vectorAUuid'], {})
            vectorBMetadata = history.get(l['vectorBUuid'], {})
            mergedVectorParams = merge(list(vectorAMetadata.keys()), list(vectorBMetadata.keys()))
            if (len(mergedVectorParams)):
                allParameters = merge(allParameters, mergedVectorParams)
                linksWithParameters.append(l)
    
        allParameters.sort()
        
        for paramNum, param in enumerate(allParameters, start=0):
            leftOffset = paramNum * Reporter.GRAPH_WIDTH + Reporter.LABEL_DEPTH
            drawLabel(param, param, False, leftOffset, 0, Reporter.GRAPH_WIDTH, Reporter.LABEL_DEPTH)
    
        for linkNum, link in enumerate(linksWithParameters):
            topOffset = linkNum * Reporter.GRAPH_HEIGHT + Reporter.LABEL_DEPTH
            
            h1Name = hosts[link['hostAUuid']]
            h2Name = hosts[link['hostBUuid']]
            linkName = '{} <-> {}'.format(h1Name, h2Name)
            linkUuid = link['uuid']
 
            vectorAMetadata = history.get(link['vectorAUuid'], {})
            vectorBMetadata = history.get(link['vectorBUuid'], {})
            
            message('Creating graphs for {} link ({} of {})'.format(linkName, linkNum + 1, len(linksWithParameters)))
            drawLabel(linkUuid, linkName, True, 0, topOffset, Reporter.LABEL_DEPTH, Reporter.GRAPH_HEIGHT)
            
            for paramNum, paramName in enumerate(allParameters, start=0):
                leftOffset = paramNum * Reporter.GRAPH_WIDTH + Reporter.LABEL_DEPTH
                
                graphData = []
                graphName = '{}#{}'.format(linkUuid, paramName)
                graphTitle = '{} \n {}'.format(linkName, paramName)
                
                # Append vector A data
                if paramName in vectorAMetadata:
                    for index, table in vectorAMetadata[paramName].items():
                        xRng = table.getColRange(ds, 1)
                        yRng = table.getColRange(ds, 2)
                    
                        graphData.append({
                            'lineName': 'vector A ({})'.format(index),
                            'XRange': xRng,
                            'YRange': yRng
                        })
                
                # Append vector B data
                if paramName in vectorBMetadata:
                    for index, table in vectorBMetadata[paramName].items():
                        xRng = table.getColRange(ds, 1)
                        yRng = table.getColRange(ds, 2)
                        
                        graphData.append({
                            'lineName': 'vector B ({})'.format(index),
                            'XRange': xRng,
                            'YRange': yRng
                        })
                
                if len(graphData) > 0:
                    drawGraph(graphName, graphTitle, graphData, leftOffset, topOffset, Reporter.GRAPH_WIDTH, Reporter.GRAPH_HEIGHT)
            
if __name__ == "__main__":
    rc = main()
    if rc:
        sys.exit(rc)
    sys.exit(0)