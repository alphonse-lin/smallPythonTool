import matplotlib.pyplot as plt
import geopandas
import shapely
from shapely.geometry import Point, Polygon, shape, MultiLineString, LineString
import time
import math
import os


def exportGeoJSON(gdf, outputPath):
    gdf.crs = {"init": "epsg:32650"}
    gdf = gdf.to_crs({"init": "epsg:4326"})
    gdf.to_file(outputPath, driver='GeoJSON')
    print("输出完成")


def timeCount(calcMode, t_start):
    t_end = time.time()
    final_time = round((t_end - t_start), 2)
    print("{0}: {1} s".format(calcMode, final_time))


def export(gdf, outputPath):
    gdf.crs = {"init": "epsg:32650"}
    gdf = gdf.to_crs({"init": "epsg:4326"})
    gdf.to_file(outputPath, driver='GeoJSON')
    print("输出文件，路径为{0}".format(outputPath))


def multiline2Line(line):
    if type(line) == MultiLineString:
        new_line = [x for x in line][0]
    else:
        new_line = line
    return new_line

def convertGeometryCoords(gdf, firstEPSG, secondEPSG):
    gdf.crs = {"init": "epsg:" + str(firstEPSG)}
    new_gdf = gdf.to_crs({"init": "epsg:" + str(secondEPSG)})
    return new_gdf

if __name__ == '__main__':
    '''设计参数部分'''
    bufferDis = -20
    inputPath=r'E:\OneDrive\桌面'
    outputPath=r'E:\114_temp\008_代码集\001_python\smallPythonTool\NetworkX_test\originalData\fileExport'
    files = os.listdir(inputPath)
    for file in files:
        if file.endswith('.geojson'):
            if not os.path.isdir(file):
                geojson = os.path.join(inputPath, file)
                exportPath = os.path.join(outputPath, file)
                if not os.path.isfile(exportPath):
                    '''计算时间'''
                    t_start = time.time()

                    '''读取shp文件_行政区边界+路网数据'''
                    # shp = r'测试数据\shapefile\sz.shp'
                    # shp = r'测试数据\shapefile\shenzhen_osmroad.shp'

                    # sz= geopandas.GeoDataFrame.from_file(shp,encoding = 'utf-8')
                    # road = geopandas.GeoDataFrame.from_file(shp,encoding = 'utf-8')

                    '''读取geojson文件_路网数据'''
                    szRoad = geopandas.read_file(geojson)
                    szRoad = convertGeometryCoords(szRoad, 4326, 32650)
                    timeCount('读取文件耗时', t_start)

                    '''是否加和 行政区边界 和 路网 数据'''
                    # lines=list(road['geometry'])+list(sz.boundary)

                    '''提取地块'''
                    lines = [multiline2Line(x) for x in szRoad['geometry']]
                    merged_lines = shapely.ops.linemerge(lines)
                    boder_lines = shapely.ops.unary_union(merged_lines)
                    decomposition = shapely.ops.polygonize_full(boder_lines)
                    timeCount('提取地块耗时', t_start)

                    '''对路进行buffer'''
                    area = geopandas.GeoDataFrame({'geometry': list(decomposition[0])})
                    area1 = area.buffer(bufferDis)
                    area1 = area1[-area1.is_empty]
                    area1 = geopandas.GeoDataFrame({'geometry': area1})
                    timeCount('buffer耗时', t_start)

                    # area1.plot()
                    # plt.show()

                    '''输出数据'''
                    # polygons = decomposition[0]
                    # polygons = [x for x in polygons]

                    '''输出geojson'''
                    exportGeoJSON(area1, exportPath)

                    t_end = time.time()
                    timeCount('{0}计算耗时'.format(file), t_start)
                    print(exportPath)

    timeCount('最终计算时间', t_start)
