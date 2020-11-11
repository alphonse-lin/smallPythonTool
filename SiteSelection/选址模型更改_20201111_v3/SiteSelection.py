#  人口合理容量 * 容积率 = 人口数
#  服务半径 ： 1000米

import json
import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import datetime
from sklearn.cluster import MeanShift, KMeans
from shapely.geometry import Point, Polygon, MultiPolygon
from geopandas import GeoDataFrame, read_file
import os


#  人数估计
def get_people(area, floor):
    if floor >= 1 and floor <= 3:
        people = (int)(area / 36)
    elif floor >= 4 and floor <= 6:
        people = (int)(area / 30)
    elif floor >= 7 and floor <= 9:
        people = (int)(area / 21)
    elif floor >= 10 and floor <= 18:
        people = (int)(area / 17)
    elif floor >= 19 and area <= 26:
        people = (int)(area / 13)
    else:
        people = (int)(area / 10)

    return people


#  找到多边形中心点（作为建筑物的点坐标）
def center_geolocation(polygon, floors):
    center_points = []
    point_people = []
    for i in range(len(polygon)):
        area = polygon[i].area
        people = get_people(area, floors[i])
        center_point = polygon[i].centroid
        center_points.append([center_point.x, center_point.y])
        point_people.append(people)

    return center_points, point_people


#  两点之间距离
def distance(lng1, lat1, lng2, lat2):
    weight = (math.sqrt(pow(abs(lng1 - lng2), 2) + pow(abs(lat1 - lat2), 2)))
    return (int)(weight)


#  学校数目估计
def school_num(info, max_label, children_num):
    group_num = []
    school_number = []
    for i in range(max_label + 1):
        group_num.append(0)
    for i in range(len(info['label'])):
        group_num[info['label'][i]] = group_num[info['label'][i]] + info['people'][i]
    for i in range(len(group_num)):
        school_number.append(group_num[i] / children_num)
    return school_number


# 把CSV的XY坐标的坐标系转化
def convertCoordsOfCSV(df, firstEPSG, secondEPSG):
    geo_points = [Point(x, y) for x, y in zip(df["x"], df["y"])]
    df_data = df.drop(["x", "y"], axis=1)
    new_df = GeoDataFrame(df_data, geometry=geo_points, crs={"init": "epsg:" + str(firstEPSG)})
    new_df = new_df.to_crs({"init": "epsg:" + str(secondEPSG)})
    all_x = [a.x for a in new_df.geometry]
    all_y = [a.y for a in new_df.geometry]
    new_df = new_df.drop(["geometry"], axis=1)
    new_df = pd.DataFrame(new_df)
    new_df["x"] = all_x
    new_df["y"] = all_y
    return new_df


def convertGeometryCoords(gdf, firstEPSG, secondEPSG):
    gdf.crs = {"init": "epsg:" + str(firstEPSG)}
    new_gdf = gdf.to_crs({"init": "epsg:" + str(secondEPSG)})
    return new_gdf


# 增加ID
def AddIndex(input_file, output_path, outputname):
    gdf = read_file(input_file)
    for i in range(len(gdf['Id'])):
        gdf.loc[i, 'Id'] = i
    exportGeoJSON(gdf, output_path, outputname)


# 输出模块
def exportCSV(df, outputPath, output_name):
    output_path = outputPath + "/{0}.csv".format(output_name)
    df.to_csv(output_path, header=True)


def exportGeoJSON(gdf, outputPath, output_name):
    # gdf.crs = {"init": "epsg:32650"}
    # gdf = gdf.to_crs({"init": "epsg:4326"})
    output_path = outputPath + "/{0}.geojson".format(output_name)
    gdf.to_file(output_path, driver='GeoJSON')
    print("geojson完成")


def multipolygon2Polygon(el):
    if type(el) == MultiPolygon:
        new_el = [x for x in el][0]
    else:
        new_el = el
    return new_el


def polygon2List(el):
    ext = el.exterior
    temp = [[x, y] for x, y in zip(ext.xy[0], ext.xy[1])]
    temp = [temp]
    return temp


#  计算模块
def cluster_calculation(filename, outputPath):
    data = read_file(filename)
    data = convertGeometryCoords(data, 4326, 32650)
    #  楼层转化与人口呈线性关系
    points = []
    buildingIds = []
    info = {'floor': [], 'point': [], 'buildingId': []}
    info['floor'] = list(data['Floor'])
    info['buildingId'] = list(data['Id'])

    temp = [multipolygon2Polygon(x) for x in data.geometry]
    center_points, point_people = center_geolocation(temp, info['floor'])
    info['point'] = center_points
    info['people'] = point_people
    for i in range(len(info['floor'])):
        for j in range(info['floor'][i]):
            points.append(center_points[i])
            buildingIds.append(info['buildingId'][i])
    datas = tuple(points)

    #  Meanshift均值偏移算法聚类
    ms = MeanShift(bandwidth=430, bin_seeding=True)
    ms.fit(datas)
    labels = ms.labels_
    cluster_centers = ms.cluster_centers_

    u, indices = np.unique(points, return_index=True, axis=0)
    labels_list = labels[indices]
    id_list = np.array(buildingIds)[indices]
    labels_unique = np.unique(labels)
    n_clusters_ = len(labels_unique)

    # 输出
    # # 输出第一次聚类中心点
    # df_centerPt1st = pd.DataFrame(columns=['x', 'y'])
    # for i in range(len(cluster_centers)):
    #     df_centerPt1st = df_centerPt1st.append({'x': cluster_centers[i][0], 'y': cluster_centers[i][1]},
    #                                            ignore_index=True)
    # df_centerPt1st = convertCoordsOfCSV(df_centerPt1st, 32650, 4326)
    # exportCSV(df_centerPt1st, outputPath, 'output1st_centerPt')

    # # 输出第一次聚类，建筑id及所属组团
    df_buildings = pd.DataFrame(columns=['clusterNo.', 'Id'])
    for i in range(len(u)):
        df_buildings = df_buildings.append(
            {'clusterNo.': labels_list[i], 'Id': id_list[i]},
            ignore_index=True)

    data=data.merge(df_buildings, on="Id")
    exportGeoJSON(data, outputPath, 'buildings_part_output')
    first_cluster_time = datetime.datetime.now()

    #  第一次聚类画图
    # plt.figure(1)
    # plt.clf()

    max_label = max(labels)
    colors = ['b', 'c', 'g', 'm', 'r', 'k', 'y', 'gray', 'lightcoral', 'bisque', 'darkorange', 'gold', 'lime', 'cyan',
              'indigo', 'royalblue']
    color = []

    last_point = [0, 0]
    label = []
    group_points = []
    group_people = []

    for i in range(max_label + 1):
        group_points.append([])
        group_people.append([])

    for i in range(len(points)):
        if last_point != points[i]:
            label.append(labels[i])
            last_point = points[i]
            color.append(colors[labels[i]])
    info['label'] = label

    for i in range(len(info['point'])):
        group_points[info['label'][i]].append(info['point'][i])
        group_people[info['label'][i]].append(info['people'][i])

    x, y = [], []

    for point in info['point']:
        x.append(point[0])
        y.append(point[1])

    # for k, col in zip(range(n_clusters_), colors):
    #     my_members = labels == k
    #     cluster_center = cluster_centers[k]
    #     plt.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col, markeredgecolor='k', markersize=14)
    #     plt.scatter(x, y, c=color, s=7)
    # plt.title('Estimated number of clusters: %d' % n_clusters_)
    # plt.show()

    schools = school_num(info, max_label, 1000)
    second_group_points = []
    second_group_people = []

    for i in range(len(schools)):
        kmeans = KMeans(n_clusters=(int)(schools[i]), random_state=0).fit(group_points[i])
        k_labels = kmeans.labels_
        for k, col in zip(range((int)(schools[i])), colors):
            points, x, y = [], [], []
            people = 0
            for j in range(len(k_labels)):
                if (k_labels[j] == k):
                    point = []
                    people += group_people[i][j]
                    point.append(group_points[i][j][0]), x.append(group_points[i][j][0])
                    point.append(group_points[i][j][1]), y.append(
                        group_points[i][j][1])  # my_members是布尔型的数组（用于筛选同类的点，用不同颜色表示）
                    points.append(point)
            second_group_points.append(points)
            second_group_people.append(people)
            cluster_center = kmeans.cluster_centers_[k]
            plt.plot(x, y, 'w', markerfacecolor=col, marker='.')  # 将同一类的点表示出来
            # plt.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,markeredgecolor='k', marker='o')  # 将聚类中心单独表示出来

    second_cluster_time = datetime.datetime.now()

    centers = []
    for points in second_group_points:
        center_point = []
        minw = 99999999999999
        for j in range(len(points)):
            sum_distance = 0
            for k in range(len(points)):
                sum_distance += distance(points[j][0], points[j][1], points[k][0], points[k][1])
            if minw > sum_distance:
                minw = sum_distance
                center_point = points[j]
        centers.append(center_point)

    finish_time = datetime.datetime.now()

    # 第二次聚类画图
    # for center in centers:
    #     plt.plot(center[0], center[1], 'o', markerfacecolor=col, markeredgecolor='k', marker='o')
    # plt.show()

    # 输出
    df_centerPt2nd = pd.DataFrame(columns=['x', 'y', 'people'])
    for i in range(len(second_group_people)):
        if second_group_people[i] > 500:
            df_centerPt2nd = df_centerPt2nd.append(
                {'x': centers[i][0], 'y': centers[i][1], 'people': second_group_people[i]},
                ignore_index=True)
    df_centerPt2nd = convertCoordsOfCSV(df_centerPt2nd, 32650, 4326)
    exportCSV(df_centerPt2nd, outputPath, 'output2nd_centerPt')

    print("总运行时间：" + (str)(finish_time - start_time))
    print("第一次聚类时间" + (str)(first_cluster_time - start_time))
    print("第二次聚类时间" + (str)(second_cluster_time - first_cluster_time))


if __name__ == '__main__':
    start_time = datetime.datetime.now()
    filename_original = 'buildings_part.geojson'
    filename_addIndex = './outputFile/buildings_part_output.geojson'
    output_path = './outputFile'

    # 计算模块
    AddIndex(filename_original, output_path, outputname='buildings_part_output')
    try:
        cluster_calculation(filename_addIndex, output_path)
    except IOError:
        print("File is not accessible.")
