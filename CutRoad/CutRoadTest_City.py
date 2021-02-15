import time
import geopandas as gpd


def timeCount(calcMode, t_start):
    t_end = time.time()
    final_time = round((t_end - t_start), 4)
    print("{0}: {1} s".format(calcMode, final_time))


def exportGeoJSON(gdf, outputPath):
    gdf.crs = {"init": "epsg:4326"}
    gdf.to_file(outputPath, driver='GeoJSON',encoding='utf8')


def roadCluster(list, roads):
    roadList = roads.loc[list,]
    return roadList


def sortData(road, province, path,t_start):
    newGdf = gpd.sjoin(road, province, op='intersects')
    newGdf =newGdf.reset_index().drop(["index"], axis=1)
    timeCount('sjoin结束', t_start)
    indexs = newGdf.index_right.values
    temp = list(set(indexs))
    # timeCount('getIndexRight', t_start)
    for j in range(len(temp)):
        exportPath = "{0}\{1}.geojson".format(path, province.loc[temp[j],"市"])
        indexList = [i for i,x in  enumerate(indexs) if x == temp[j]]
        singleRoad = roadCluster(indexList, newGdf)
        # singleRoad = gpd.GeoDataFrame({"geometry": singleRoad.geometry})

        exportGeoJSON(singleRoad, exportPath)
        timeCount("{0}输出完成".format(province.loc[temp[j],"市"]),t_start)


if __name__ == '__main__':
    t_start = time.time()

    roadPath = r'F:\001_数据集\Data\003_城市路网\005_OSM\中国道路网2019\gis_osm_roads_free_1.shp'
    # roadPath = r'D:\OneDrive\Documents\实验室\CAAD\126_中心路网提取\Utilis\CutRoad\input\hainanTestRoad.shp'
    provincePath = r'E:\114_temp\015_DEMData\tets003\CASER\QGIS打点\太原路网\shanxi_region.shp'
    outputPath = r'E:\114_temp\015_DEMData\tets003\CASER\QGIS打点\太原路网'

    road= gpd.read_file(roadPath,encoding='utf8')
    province = gpd.read_file(provincePath,encoding='utf8')
    # road=road_notCRS.to_crs({"init": "epsg:32650"})
    # province=province_notCRS.to_crs({"init": "epsg:32650"})
    timeCount('读取结束', t_start)

    sortData(road, province, outputPath,t_start)
    timeCount('存储处理结束', t_start)

    # # polygon['id']=range(0, len(polygon))
    # # exportGeoJSON(polygon, os.path.join(outputPath, 'finalOutput.geojson'))
