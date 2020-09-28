import itertools
from operator import itemgetter

import geopandas

from shapely.geometry import Point, LineString
from shapely.geometry import box

import rtree.index
import time


def timeCount(calcMode, t_start):
    t_end = time.time()
    final_time = round((t_end - t_start), 2)
    print("{0}模块：计算时间 {1} s".format(calcMode, final_time))

def export(gdf, outputPath):
    # gdf.crs = {"init": "epsg:32650"}
    # gdf = gdf.to_crs({"init": "epsg:4326"})
    gdf.to_file(outputPath, driver='GeoJSON')
    print("\n输出文件，路径为{0}".format(outputPath))

def rTreeCreate(dataList):
    index = rtree.index.Index()
    for i in range(len(dataList)):
        geom = roadOri['geometry'][i]
        index.insert(i, geom.bounds)
    return index

def boudningBoxCreate(shape):
    boundCollection = shape.bounds
    boundingBox = box(boundCollection[0], boundCollection[1], boundCollection[2], boundCollection[3])
    return boundingBox

def middlePtGet(shape):
    pointList = [[x, y] for x, y in zip(shape.exterior.xy[0], shape.exterior.xy[1])]
    return pointList

def nearestLineIndexGet(pointList, indexRT):
    fidsList = []
    for i in range(len(pointList) - 1):
        midPt = LineString([pointList[i], pointList[i + 1]]).interpolate(0.5, normalized=True)
        fids = [int(j) for j in indexRT.nearest(midPt.bounds)]
        fidsList.append(fids[0])
    return fidsList

def blockValueGet(fidsList, gdf):
    btValue = []
    clValue = []
    for fidIndex in fidsList:
        btValue.append(gdf.loc[fidIndex, 'betweenness'])
        clValue.append(gdf.loc[fidIndex, 'closeness'])
    btSum=sum(btValue)
    clSum=sum(clValue)
    return btSum, clSum

def blocksValueGet(polygons, index):
    btResult = []
    clResult = []
    for polygon in polygons:
        # 创建boundingbox
        boundingBox = boudningBoxCreate(polygon)

        # 提取bounding box线，及中点
        pointList = middlePtGet(boundingBox)

        # 搜索最近线段，返回index
        fidsList = nearestLineIndexGet(pointList, index)

        # 按照index，抽取特定数值，并加和
        btSum, clSum = blockValueGet(fidsList, roadOri)

        btResult.append(btSum)
        clResult.append(btSum)

    return btResult, clResult

if __name__ == '__main__':
    t_start = time.time()

    roadFile = './originalData/road_BT+CL.geojson'
    blockFile = './originalData/fileExport/block.geojson'
    outputPath = './originalData/fileExport/newBlockResult_BT+CL.geojson'
    timeCount('读取', t_start)

    roadOri = geopandas.read_file(roadFile)
    blockOri = geopandas.read_file(blockFile)
    polygons = blockOri['geometry']

    # 创建R tree
    index = rTreeCreate(roadOri)
    timeCount('Rtree创建', t_start)

    # 将线的数值，匹配到地块上
    btResult, clResult=blocksValueGet(polygons, index)
    timeCount('匹配计算', t_start)

    # 输出
    blockOri['betweenness'] = btResult
    blockOri['closeness'] = clResult
    export(blockOri, outputPath)

    timeCount('最终计算时间', t_start)
