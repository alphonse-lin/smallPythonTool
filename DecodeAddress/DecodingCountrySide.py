import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry.point import Point


def geocode(address):
    parameters = {'address': address, 'key': '34b0bbcfc3236cee8a53fdf28ba768ec'}
    # parameters = {'address': address, 'key': 'b39b53bbb87710ac7741609ea45e3e31'}
    base = 'http://restapi.amap.com/v3/geocode/geo'
    response = requests.get(base, parameters)
    answer = response.json()
    return answer


if __name__ == '__main__':
    filePath = r'E:\114_temp\008_代码集\001_python\smallPythonTool\DecodeAddress\input\长治县选点3.xlsx'
    outputPath= r'E:\114_temp\008_代码集\001_python\smallPythonTool\DecodeAddress\output\长治县选点3_new_result.csv'
    data = pd.read_excel(filePath, sheet_name='Sheet1')

    # results = data['地域分布/地理信息']
    results = data['地理位置']
    geometry = []
    for i in range(len(results)):
        if pd.isna(results[i]):
            data.loc[i, 'lon'] = 0
            data.loc[i, 'lat'] = 0

        else:
            # result_temp='{0},{1}'.format(results[i].split(',')[1],results[i].split(',')[2])
            # print(result_temp)
            result = geocode(results[i].split(',')[0])
            if result['count'] == '1':
                # print(result)
                print(results[i] + result['geocodes'][0]['location'])
                addressCode = result['geocodes'][0]['location'].split(',')
                # geometry.append(Point(float(addressCode[0]),float(addressCode[1])))

                data.loc[i, 'lon'] = float(addressCode[0])
                data.loc[i, 'lat'] = float(addressCode[1])
            else:
                data.loc[i, 'lon'] = 0
                data.loc[i, 'lat'] = 0

    data.to_csv(outputPath, encoding='utf8')

# data=data.rename(
#     columns={"建筑名称": "name", "位置": "location", "年代": "year", "研究方向": "researchDirection", "形制": "xingZhi", "专著": "zhuanZhu"})
# geometry = [Point(xy) for xy in zip(data.lon, data.lat)]
#
# data = data.drop(['lon', 'lat'], axis=1)
# gdf = gpd.GeoDataFrame(data, crs={"init": "EPSG:4326"}, geometry=geometry)
#
# # gdf=['name','location','year','research_direction', 'xing_zhi','zhuan_zhu']
# print(gdf)
# gdf.to_file(outputPath_shp, driver='ESRI Shapefile',encoding='utf8')
#
# from pandas import DataFrame
# temp = DataFrame(gdf)