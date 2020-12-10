import time
import geopandas as gpd
import os


def timeCount(calcMode, t_start):
    t_end = time.time()
    final_time = round((t_end - t_start), 4)
    print("{0}: {1} s".format(calcMode, final_time))


def exportGeoJSON(gdf, outputPath):
    gdf.crs = {"init": "epsg:32650"}
    gdf.to_file(outputPath, driver='GeoJSON', encoding='utf8')


if __name__ == '__main__':
    t_start = time.time()

    inputPath = r'C:\Users\dell\Desktop\20201210-中心线'
    outputPath = r'C:\Users\dell\Desktop\20201210-中心线\简化'
    files = os.listdir(inputPath)
    s = []
    print(len(files))

    for file in files:
        if not os.path.isdir(file):
            if file.endswith('geojson'):
                roadPath = os.path.join(inputPath, file)
                exportPath = os.path.join(outputPath, file)
                if not os.path.isfile(exportPath):
                    road = gpd.read_file(roadPath, encoding='unicode_escape')
                    timeCount('读取结束', t_start)
                    road = gpd.GeoDataFrame({"geometry": road.geometry})
                    timeCount('处理结束', t_start)

                    exportGeoJSON(road, exportPath)
                timeCount("{0}存储完成".format(file), t_start)
