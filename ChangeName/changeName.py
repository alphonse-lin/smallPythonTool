# -*- coding: gbk -*-
import geopandas as gpd

shpFile = r"E:\OneDrive\Documents\ʵ����\CAAD\114_temp\008_�ƾ�ƽ̨����\��������\�Դ��۰�����\XAblockData.shp"
shp2File = r"E:\OneDrive\Documents\ʵ����\CAAD\114_temp\008_�ƾ�ƽ̨����\��������\�Դ��۰�����\XAblockData_output.shp"
gdf = gpd.read_file(shpFile, encoding='gbk')
test = "�õ�����"
gdf["�õ�����"] = gdf["landUse"]
print(gdf)

gdf.to_file(shp2File, encoding='gbk')
# gdf2 = gdf.rename(columns={"landUse": "�õ�����"})
#
# gdf2.to_file(shp2File, encoding='gbk')
