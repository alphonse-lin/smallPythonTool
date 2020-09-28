import time
import geopandas as gpd
import pandas
import os
from collections import Counter


def timeCount(calcMode, t_start):
    t_end = time.time()
    final_time = round((t_end - t_start), 4)
    print("{0}: {1} s".format(calcMode, final_time))


def exportGeoJSON(gdf, outputPath):
    gdf.crs = {"init": "epsg:4326"}
    gdf.to_file(outputPath, driver='GeoJSON')
    print("输出完成")


def clusterCount(list, points):
    strList=points.loc[list,'typecode']
    numCount = Counter(strList)
    # timeCount('clusterCount', t_start)
    return numCount


def sortData(point, polygon):
    newGdf = gpd.sjoin(point, polygon, op='within')
    timeCount('sjoin结束', t_start)
    indexs = newGdf.index_right.values
    temp = list(set(indexs))
    # timeCount('getIndexRight', t_start)

    ncKeyList=[]
    ncItemList=[]
    GIDList=[]

    for j in range(len(temp)):
        indexList = [i for i, x in enumerate(indexs) if x == temp[j]]
        numCount = clusterCount(indexList, point)

        ncKey=list(numCount.keys())
        ncItem=list(numCount.values())
        GID=[temp[j]]*len(ncItem)

        ncKeyList.extend(ncKey)
        ncItemList.extend(ncItem)
        GIDList.extend(GID)
        timeCount('{0}: 地块内循环'.format(j), t_start)

    finalDF=pandas.DataFrame({'GID':GIDList, 'typeCode':ncKeyList,'count':ncItemList})

    timeCount('遍历时间', t_start)
    return finalDF


if __name__ == '__main__':
    t_start = time.time()
    # pointPath = r'.\testFile\partPOI.shp'
    # polygonPath = r'.\testFile\partPolygon.shp'
    pointPath = r'D:\OneDrive\Documents\实验室\CAAD\126_中心路网提取\Utilis\POI配点\testFile\wholePOI.shp'
    polygonPath = r'D:\OneDrive\Documents\实验室\CAAD\126_中心路网提取\Utilis\POI配点\testFile\wholePolygon.shp'
    outputPath = r'D:\OneDrive\Documents\实验室\CAAD\126_中心路网提取\Utilis\POI配点\outputFile'

    point = gpd.read_file(pointPath)
    polygon = gpd.read_file(polygonPath)
    timeCount('读取结束', t_start)

    resultDF = sortData(point, polygon)
    timeCount('数据处理结束', t_start)

    resultDF.to_csv(os.path.join(outputPath, 'finalOutput_2.csv'), index=False)

    # # polygon['id']=range(0, len(polygon))
    # # exportGeoJSON(polygon, os.path.join(outputPath, 'finalOutput.geojson'))

    timeCount('结束计算耗时', t_start)
