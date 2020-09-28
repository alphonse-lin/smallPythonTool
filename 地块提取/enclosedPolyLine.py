# import fiona
# from shapely.geometry import shape, mapping, Polygon, LineString
# import geopandas as gpd
#
# file = r'测试数据\test.shp'
# output = r'测试数据\test_output.shp'
#
# schema = {
#     'geometry': 'Polygon',
#     'properties' : {'id':'int'}
# }
#
# with fiona.open(file) as in_file, fiona.open(output, 'w', 'ESRI Shapefile', schema) as out_file:
#     for index_line, row in enumerate(in_file):
#         line = shape(row['geometry'])
#         coordinates = []
#
#         if isinstance(line, LineString):
#             for index, point in enumerate(line.coords):
#                 if index == 0:
#                     first_pt = point
#                 coordinates.append(point)
#
#             coordinates.append(first_pt)
#             if len(coordinates) >= 3:
#                 polygon = Polygon(coordinates)
#                 print(polygon)
#                 out_file.write({
#                     'geometry': mapping(polygon),
#                     'properties': {'id': index_line},
#                 })
#             else:
#                 print("no higher than 3")

import geopandas as gpd
import shapely.geometry as geom


def polyline_to_polygon(input_file, output_file):
    gdf = gpd.read_file(input_file)
    gdf['geometry'] = gdf['geometry'].apply(lambda x: geom.Polygon(x.coords))
    # in order to have donut geometries, subset polygons from each others
    for index in list(gdf.index):
        indices = list(gdf.index)
        indices.remove(index)
        for index_ in indices:
            try:
                gdf.loc[index, 'geometry'] = gdf.loc[index, 'geometry'].difference(gdf.loc[index_, 'geometry'])
            except ValueError:
                pass
    gdf.to_file(output_file)


if __name__ == '__main__':
    file = r'测试数据/test.shp'
    output = r'测试数据\test_output.shp'
    polyline_to_polygon(file, output)
