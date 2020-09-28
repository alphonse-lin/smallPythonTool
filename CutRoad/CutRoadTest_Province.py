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
        exportPath = "{0}\{1}_乡镇村道路.geojson".format(path, province.loc[temp[j],"省"])
        indexList = [i for i,x in  enumerate(indexs) if x == temp[j]]
        singleRoad = roadCluster(indexList, newGdf)

        exportGeoJSON(singleRoad, exportPath)
        timeCount("{0}输出完成".format(province.loc[temp[j],"省"]),t_start)


if __name__ == '__main__':
    t_start = time.time()

    roadPath = r'D:\OneDrive\Documents\实验室\CAAD\126_中心路网提取\Utilis\CutRoad\input\乡镇村_CRS.shp'
    # roadPath = r'D:\OneDrive\Documents\实验室\CAAD\126_中心路网提取\Utilis\CutRoad\input\hainanTestRoad.shp'
    provincePath = r'D:\OneDrive\Documents\实验室\CAAD\126_中心路网提取\Utilis\CutRoad\input\区划\省.shp'
    outputPath = r'D:\OneDrive\Documents\实验室\CAAD\126_中心路网提取\Utilis\CutRoad\output_导航数据\乡镇村道路'

    road_notCRS = gpd.read_file(roadPath,encoding='utf8')
    province_notCRS = gpd.read_file(provincePath,encoding='utf8')
    road=road_notCRS.to_crs({"init": "epsg:4326"})
    province=province_notCRS.to_crs({"init": "epsg:4326"})
    timeCount('读取结束', t_start)

    sortData(road, province, outputPath,t_start)
    timeCount('存储处理结束', t_start)

    # # polygon['id']=range(0, len(polygon))
    # # exportGeoJSON(polygon, os.path.join(outputPath, 'finalOutput.geojson'))
