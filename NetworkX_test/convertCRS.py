import geopandas

def export(gdf, outputPath):
    gdf.crs = {"init": "epsg:32650"}
    gdf = gdf.to_crs({"init": "epsg:4326"})
    gdf.to_file(outputPath, driver='GeoJSON')
    print("输出文件，路径为{0}".format(outputPath))


if __name__ == '__main__':
    geojson = r'C:\Users\CAUPD-BJ141\Downloads\唐山规划图纸.geojson'
    szRoad = geopandas.read_file(geojson)
    outputPath = './roadCRS.geojson'

    export(szRoad, outputPath)