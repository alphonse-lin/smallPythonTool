import shapefile
import time
import  os
import geopandas as gpd

def timeCount(calcMode, t_start):
    t_end = time.time()
    final_time = round((t_end - t_start), 4)
    print("{0}: {1} s".format(calcMode, final_time))
#
# def exportGeoJSON(gdf, outputPath):
#     gdf.crs = {"init": "epsg:4326"}
#     gdf.to_file(outputPath, driver='GeoJSON', encoding='utf-8')
#     print("输出完成")
#
# t_start = time.time()
#
# inputPath=r'D:\实验室\Data\42城市06\shp文件'
# outputPath=r'D:\实验室\Data\003_城市路网\002_导航数据\全国_导航数据_按省份\output'
# files=os.listdir(inputPath)
# s=[]
# print(len(files))
#
# for file in files:
#     if not os.path.isdir(file):
#         roadPath=os.path.join(inputPath,file)
#         exportPath=os.path.join(outputPath,file)
#         if not os.path.isfile(exportPath):
#
#             road = gpd.read_file(roadPath, encoding='utf8')
#             road = gpd.GeoDataFrame({"geometry":road.geometry\
#                                      ,"FuncClass": road["FuncClass"]\
#                                      ,"Direction": road["Direction"]\
#                                      ,"Kind":road["Kind"]}
#                                     )
#
#             exportGeoJSON(road, exportPath)
#         timeCount("{0}存储完成".format(file), t_start)


t_start = time.time()

roadPath = r'D:\实验室\Data\42城市06\shp文件\42cities.shp'
outputPath = r'D:\实验室\Data\42城市06\shp文件缩小'

r = shapefile.Reader(roadPath, encoding="unicode_escape")

w = shapefile.Writer(outputPath, encoding="unicode_escape")
w.field("FuncClass")
w.field("Direction")
w.field("Kind")

for shaperec in r.iterShapeRecords():
    w.shape(shaperec.shape)
    w.record(shaperec.record[9], shaperec.record[12], shaperec.record[14])
    # w.record(shaperec.record[9])

w.close()
timeCount("存储完成",t_start)