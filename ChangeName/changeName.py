# -*- coding: gbk -*-
import geopandas as gpd

shpFile = r"E:\OneDrive\Documents\实验室\CAAD\114_temp\008_浩鲸平台开发\最终数据\自创雄安数据\XAblockData.shp"
shp2File = r"E:\OneDrive\Documents\实验室\CAAD\114_temp\008_浩鲸平台开发\最终数据\自创雄安数据\XAblockData_output.shp"
gdf = gpd.read_file(shpFile, encoding='gbk')
test = "用地属性"
gdf["用地属性"] = gdf["landUse"]
print(gdf)

gdf.to_file(shp2File, encoding='gbk')
# gdf2 = gdf.rename(columns={"landUse": "用地属性"})
#
# gdf2.to_file(shp2File, encoding='gbk')
