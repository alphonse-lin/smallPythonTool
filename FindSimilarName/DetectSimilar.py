import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry.point import Point
import difflib


# 判断相似度的方法，用到了difflib库
def get_equal_rate_1(str1, str2):
    return difflib.SequenceMatcher(None, str1, str2).quick_ratio()


if __name__ == '__main__':
    filePath = r'E:\114_temp\001_古道\赵一一的建筑年代形制学\表格\晋东南地区五代、宋、金木构建筑的外檐铺作属性_页面_1.xlsx'
    data1 = pd.read_excel(filePath, sheet_name='test001')
    data2 = pd.read_excel(filePath, sheet_name='test002')

    results1 = data1['建筑名称']
    results1_id = data1['ID']
    results2 = data2['建筑名称']
    results2_id = data2['ID']
    move = dict.fromkeys((ord(c) for c in u"\xa0\n\t"))
    length=0
    for i in range(len(results2)):
        for j in range(len(results1)):
            c_str1 = str(results1[j]).translate(move)
            # if (str(results2[i]) == c_str1):
            ratio=get_equal_rate_1(str(results2[i]),c_str1)
            if(ratio>0.6):
                print("ID号为{0}：{1}_：{2}__{3}".format(results2_id[i], results2[i], results1_id[j], c_str1))
        length += 1

        # for j in range(len(results1)):
        #     c_str1 = str(results1[j]).translate(move)
        #     # if (str(results2[i]) == c_str1):
        #     ratio=get_equal_rate_1(str(results2[i]),c_str1)
        #     if(ratio>0.6):
        #         similar_list.append(ratio)
        #         similar_index_dic.update({ratio:j})
        # if(len(similar_list)!=0):
        #     length += 1
        #     print("ID号为{0}：{1}_：{2}".format(results2_id[i], results2[i], results1_id[similar_index_dic[max(similar_list)]]))


    print("相似个数{0}".format(length))
