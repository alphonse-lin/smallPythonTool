import geopandas as gpd
import pandas as pd

inputFilePath = r'E:\PythonFile\testFile\SelectionPOI\bj_poi.csv'
inputFilePath2 = r'E:\PythonFile\testFile\SelectionPOI\result_070500.csv'
typeCodeNum = '070500'
insideStr = '京东'
outputPath = r'E:\PythonFile\testFile\SelectionPOI\result_{0}.csv'.format(typeCodeNum)
outputNamePath = r'E:\PythonFile\testFile\SelectionPOI\name_{0}.csv'.format(insideStr)
dfFile = pd.read_csv(inputFilePath)
typeCode = dfFile['typecode']

POIIndexList = []
POINameIndex = []

# for i in range(len(typeCode)):
#     if typeCode[i] == typeCodeNum:
#         POIIndexList.append(i)
#
# outputDf = dfFile.loc[POIIndexList]

outputDf = pd.read_csv(inputFilePath2)
DfName = outputDf['name']
for j in range(len(DfName)):
    if insideStr in DfName.iloc[j]:
        POINameIndex.append(j)

outputDfName = outputDf.iloc[POINameIndex]

# outputDf.to_csv(outputPath)
outputDfName.to_csv(outputNamePath)
