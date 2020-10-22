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
from shapely.geometry import Point, Polygon


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
def center_geolocation(points, floors):
    center_points = []
    point_people = []
    for i in range(len(points)):
        polygon = Polygon(points[i][0])
        area = polygon.area
        people = get_people(area, floors[i])
        center_point = polygon.centroid
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


# 输出模块
def exportCSV(df, output_name):
    output_path = "./{0}.csv".format(output_name)
    df.to_csv(output_path, header=True)


#  计算模块
def cluster_calculation(filename, output_path_1st, output_path_2nd):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)

    #  楼层转化与人口呈线性关系
    points = []
    info = {'floor': [], 'point': []}
    for feature in data["features"]:
        info['floor'].append(feature["properties"]['Floor'])
        info['point'].append(feature["geometry"]["coordinates"][0])
    center_points, point_people = center_geolocation(info['point'], info['floor'])
    info['point'] = center_points
    info['people'] = point_people
    for i in range(len(info['floor'])):
        for j in range(info['floor'][i]):
            points.append(center_points[i])

    datas = tuple(points)

    #  Meanshift均值偏移算法聚类
    ms = MeanShift(bandwidth=430, bin_seeding=True)
    ms.fit(datas)
    labels = ms.labels_
    cluster_centers = ms.cluster_centers_

    u, indices=np.unique(points,return_index=True, axis=0)
    labels_list=labels[indices]
    labels_unique = np.unique(labels)
    n_clusters_ = len(labels_unique)

    # 输出
    # # 输出第一次聚类中心点
    df_centerPt1st = pd.DataFrame(columns=['x', 'y'])
    for i in range(len(cluster_centers)):
        df_centerPt1st = df_centerPt1st.append({'x': cluster_centers[i][0], 'y': cluster_centers[i][1]},
                                            ignore_index=True)
    exportCSV(df_centerPt1st, 'output1st_centerPt')

    # # 输出第一次聚类，建筑标签
    df_buildings = pd.DataFrame(columns=['x', 'y', 'clusterNo.'])
    for i in range(len(u)):
        df_buildings = df_buildings.append(
            {'x': u[i][0], 'y': u[i][1], 'clusterNo.': labels_list[i]},
            ignore_index=True)
    exportCSV(df_buildings, 'output1st_buildings')

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
    exportCSV(df_centerPt2nd, 'output2nd_centerPt')
    print(second_group_people)

    print("总运行时间：" + (str)(finish_time - start_time))
    print("第一次聚类时间" + (str)(first_cluster_time - start_time))
    print("第二次聚类时间" + (str)(second_cluster_time - first_cluster_time))


if __name__ == '__main__':
    start_time = datetime.datetime.now()
    filename = 'buildings_part.geojson'
    output_path_1st = './output_1st.csv'
    output_path_2nd = './output_2nd.csv'

    # 计算模块
    cluster_calculation(filename, output_path_1st, output_path_2nd)
