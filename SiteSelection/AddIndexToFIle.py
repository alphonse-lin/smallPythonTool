import shapely
import geopandas as gpd

def exportGeoJSON(gdf, outputPath):
    # gdf.crs = {"init": "epsg:32650"}
    # gdf = gdf.to_crs({"init": "epsg:4326"})
    gdf.to_file(outputPath, driver='GeoJSON')
    print("输出完成")

def AddIndex(input_file):
    gdf = gpd.read_file(input_file)
    for i in range(len(gdf['Id'])):
        gdf.loc[i, 'Id'] = i
    return gdf
    # in order to have donut geometries, subset polygons from each others

    # gdf.to_file(output_file)


if __name__ == '__main__':
    input_file = r"D:\OneDrive\Documents\实验室\CAAD\126_中心路网提取\Utilis\SiteSelection\buildings_part.geojson"
    output_file = r"D:\OneDrive\Documents\实验室\CAAD\126_中心路网提取\Utilis\SiteSelection\buildings_part_output.geojson"
    gdf=AddIndex(input_file)
    exportGeoJSON(gdf, output_file)
