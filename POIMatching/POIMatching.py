import geopandas
import os

if __name__ == '__main__':
    poiPath=r'D:\OneDrive\Documents\实验室\CAAD\126_中心路网提取\Utilis\POIMatching\data\bj_POI_Part.csv'
    listPath=r'D:\OneDrive\Documents\实验室\CAAD\126_中心路网提取\Utilis\POIMatching\data\codeList.csv'
    outputPath=r'D:\OneDrive\Documents\实验室\CAAD\126_中心路网提取\Utilis\POIMatching\data\output'

    bjPOI=geopandas.read_file(poiPath)
    codeList = geopandas.read_file(listPath)

    mergeList= codeList[['spatialTypeCode','typecode']]
    tempList=bjPOI[['id','typecode']]
    mergeList=mergeList.merge(tempList,on="typecode")

    mergeList.to_csv(os.path.join(outputPath, 'poiMatching.csv'), index=False)



