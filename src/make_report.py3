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

def message(str):
    global quiet
    if not quiet:
        print(str)
        
def merge(l1, l2):
    res = []
    for i in l1 + l2:
        if i not in res:
            res.append(i)
    return res

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


class Table:
    startCol = 0
    startRow = 0
    cols = 0
    rows = 0

class DataStore:
    lastColNum = 1
    dataSheet = None
    
    def __init__(self, sheet):
        self.dataSheet = sheet
    
    def allocateTable(self, cols):
        colNum = self.lastColNum
        rowNum = 1
        self.lastColNum += cols
        newTable = Table()
        newTable.startCol = colNum
        newTable.startRow = rowNum
        newTable.cols = cols
        newTable.rows = 0
        return newTable
    
    def writeRow(self, table, row):
        colNum = table.startCol
        rowNum = table.startRow + table.rows
        for cell in row:
            self.dataSheet.Cells(rowNum, colNum).Value = cell
            colNum += 1
        table.rows += 1

class Reporter:
    GRAPH_HEIGHT = 300
    GRAPH_WIDTH = 500
    LABEL_DEPTH = 50
    TIMESTAMP_FORMAT = '%Y.%m.%d %H:%M:%S'

    xl = wb = reportSheet = dataSheet = None

    def __init__(self):
        self.xl = win32com.client.gencache.EnsureDispatch('Excel.Application')
    
    def makeReport(self, resultFile, hostsFile, linksFile, historyFile):
        self.wb = self.xl.Workbooks.Add()
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
        metadata = {}
        dataStore = DataStore(self.dataSheet)

        def convertTimestamp(str):
            # Parse ISO 8601 timestamp
            res = str.replace('Z','+00:00')
            res = re.sub('([^.]+)(\.\d+)?([+-]\d\d):(\d\d)', '\g<1>\g<3>\g<4>', res)
            parsed = datetime.strptime(res, "%Y-%m-%dT%H:%M:%S%z").astimezone()
            return parsed.strftime(Reporter.TIMESTAMP_FORMAT)
            
        def readTSVByRow(file, fn):
            with open(file) as f:
                reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
                header = next(reader)
                for row in reader:
                    fn(dict(zip(header, row)))

        def handleHostRow(host):
            hosts[host['uuid']] = host['name']
        
        def handleLinkRow(link):
            links[link['uuid']] = link
        
        def handleHistoryRow(vector):
            uuid = vector['nmsObjectUuid']
            paramName = vector['parameterName']
            paramIndex = vector['index']
            
            value = vector['value'] if vector['value'] != 'null' else ''
            timestamp = convertTimestamp(vector['timestamp'])
            rowData = [uuid, paramName, timestamp, value]

            if uuid not in metadata:
                metadata[uuid] = {}

            if paramName not in metadata[uuid]:
                metadata[uuid][paramName] = {}

            if paramIndex not in metadata[uuid][paramName]:
                metadata[uuid][paramName][paramIndex] = dataStore.allocateTable(len(rowData))

            dataStore.writeRow(metadata[uuid][paramName][paramIndex], rowData)

        message('Reading {}'.format(hostsFile))
        readTSVByRow(hostsFile, handleHostRow)
        message('Reading {}'.format(linksFile))
        readTSVByRow(linksFile, handleLinkRow)
        message('Reading {}'.format(historyFile))
        readTSVByRow(historyFile, handleHistoryRow)
        
        return hosts, links, metadata
    
    def drawGraphs(self, hosts, links, metadata):
        rs = self.reportSheet
        ds = self.dataSheet
        
        def getColRange(table, colNum):
            col = table.startCol + colNum - 1
            row1 = table.startRow
            row2 = table.startRow + table.rows - 1
            return ds.Range(ds.Cells(row1, col), ds.Cells(row2, col))
        
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
            vectorAMetadata = metadata.get(l['vectorAUuid'], {})
            vectorBMetadata = metadata.get(l['vectorBUuid'], {})
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
 
            vectorAMetadata = metadata.get(link['vectorAUuid'], {})
            vectorBMetadata = metadata.get(link['vectorBUuid'], {})
            
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
                        xRng = getColRange(table, 3)
                        yRng = getColRange(table, 4)
                    
                        graphData.append({
                            'lineName': 'vector A ({})'.format(index),
                            'XRange': xRng,
                            'YRange': yRng
                        })
                
                # Append vector B data
                if paramName in vectorBMetadata:
                    for index, table in vectorBMetadata[paramName].items():
                        xRng = getColRange(table, 3)
                        yRng = getColRange(table, 4)
                        
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