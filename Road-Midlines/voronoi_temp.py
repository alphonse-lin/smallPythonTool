from scipy.spatial import Voronoi
from geopandas import GeoDataFrame, read_file
from shapely.ops import split
from shapely.geometry.linestring import LineString
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry import GeometryCollection
from rdp import rdp
from copy import deepcopy
from time import time
from sys import path
import numpy as np
import os


dist = 15   # Buffer distance
point_dist = 15   # Distance among points when interpolating points within lines to add more points
grid_size = 500
threshold = 30   # Threshold for the length under which lines should be deleted
rdp_eps = 10   # Epsilon value for the RDP algorithm
margin_pos = 2   # Number of digits that should be tolerated when snapping points
folder_name = 'Road-Midlines'
path.append(folder_name)
file_path = './{0}/geojson/shandong.geojson'.format(folder_name)   # Input data path
# output_path = './{0}/geojson/shandong_output.geojson'.format(folder_name)   # Output data path
# output_path = r'D:\实验室\Data\003_城市路网\009_现有单线路网数据\20200918_单线路网数据\吉林省.geojson'
from grid import Grid
from vertice import Vertice
from union_find_tree import union_find_tree


def polygons_to_point_series(myPolygonList, point_dist):
    def interpolate_points(myLine, point_dist):
        def myDist(x1, y1, x2, y2):
            return np.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))

        def interpolate_within_single_line(x1, y1, x2, y2, point_dist):
            mythreshold = 0.01
            line_dist = myDist(x1, y1, x2, y2)
            point_num = np.trunc(line_dist/point_dist)
            if np.abs(point_num*point_dist-line_dist) > mythreshold:
                point_num = point_num + 1
            delta_y = (y2 - y1) * point_dist / line_dist
            delta_x = (x2 - x1) * point_dist / line_dist
            if np.abs(x1 - x2)<mythreshold:
                x_list = np.repeat(x1, point_num)
            else:
                x_list = np.arange(x1, x2, delta_x)
            if np.abs(y1 - y2)<mythreshold:
                y_list = np.repeat(y1, point_num)
            else:
                y_list = np.arange(y1, y2, delta_y)
            len_min = min(len(x_list), len(y_list))
            x_list = x_list[0: len_min]
            y_list = y_list[0: len_min]
            all_list = np.column_stack((x_list, y_list))
            return all_list

        this_all_points = []
        myLineList = np.asarray(myLine)
        for i in range(len(myLineList)-1):
            this_len = myDist(myLineList[i][0], myLineList[i][1], myLineList[i+1][0], myLineList[i+1][1])
            if this_len <= point_dist:
                this_all_points.append(myLineList[i])
            else:
                new_points = interpolate_within_single_line(myLineList[i][0], myLineList[i][1],
                                                            myLineList[i+1][0], myLineList[i+1][1], point_dist)
                this_all_points.extend(new_points)
        this_all_points.append(myLineList[-1])
        this_all_points = np.array(this_all_points)
        return this_all_points

    all_points = []
    for myPolygon in myPolygonList:
        poly_ext_pts = interpolate_points(myPolygon.exterior, point_dist)
        all_points.extend(poly_ext_pts)

        poly_ints = list(myPolygon.interiors)
        for i in range(len(poly_ints)):
            this_pts = interpolate_points(poly_ints[i], point_dist)
            all_points.extend(this_pts)
    all_points = np.array(all_points)
    return all_points


def filter_ridges_inside_buffer(all_grids, vor, xmin, ymin, xmax, ymax, grid_size):
    def judge_ridges_buffer_intersect(all_grids, vertice_o, vertice_d):
        grid_id_range = []
        start_row = min(vertice_o.row, vertice_d.row)
        end_row = max(vertice_o.row, vertice_d.row)+1
        start_col = min(vertice_o.col, vertice_d.col)
        end_col = max(vertice_o.col, vertice_d.col)+1
        for i in range(start_row, end_row):
            for j in range(start_col, end_col):
                grid_id_range.append([i,j])

        this_line = LineString([vertice_o.point, vertice_d.point])
        this_line_sections = [this_line.intersection(all_grids[x[0], x[1]].gridPolygon) for x in grid_id_range]

        within_or_not = True
        for i in range(len(grid_id_range)):
            this_line_section = this_line_sections[i]
            if type(this_line_section) != GeometryCollection:
                this_grid_xy = grid_id_range[i]
                this_buffer_section = all_grids[this_grid_xy[0], this_grid_xy[1]].bufferUnionTrimmed
                if not this_line_section.within(this_buffer_section):
                    within_or_not = False
                    break
        return within_or_not

    verticeList = []
    point_bool_list = [False] * (len(vor.vertices)+1)
    max_point_id = 0
    for i in range(len(vor.vertices)):
        this_vertice = vor.vertices[i]
        newVertice = Vertice(all_grids, xmin, ymin, xmax, ymax, grid_size, this_vertice[0], this_vertice[1])
        verticeList.append(newVertice)
        if newVertice.withinBuffer:
            point_bool_list[i] = True
            max_point_id = i

    ridges_selected = []
    for i in range(len(vor.ridge_vertices)):
        this_ridge = vor.ridge_vertices[i]
        if (this_ridge[0] <= max_point_id) and (this_ridge[1] <= max_point_id) and (this_ridge[0] >= 0) and (this_ridge[1] >= 0):
            if point_bool_list[this_ridge[0]] and point_bool_list[this_ridge[1]]:
                if judge_ridges_buffer_intersect(all_grids, verticeList[this_ridge[0]], verticeList[this_ridge[1]]):
                    ridges_selected.append(this_ridge)
    return ridges_selected


def create_vertice_dict(ridgeList):
    uniqueList = list(set([x[0] for x in ridgeList] + [x[1] for x in ridgeList]))
    all_dict = dict((x, []) for x in uniqueList)
    for i in range(len(ridgeList)):
        this_ridge = ridgeList[i]
        all_dict[this_ridge[0]].append(this_ridge[1])
        all_dict[this_ridge[1]].append(this_ridge[0])
    return all_dict


def search_seperated_roads(myVertice):
    vertice_pointer = myVertice
    vertice_list = [myVertice]
    while (vertice_degree[vertice_pointer] == 2):
        anotherVertice = edge_dict_used[vertice_pointer][0]
        edge_dict_used[vertice_pointer].remove(anotherVertice)
        edge_dict_used[anotherVertice].remove(vertice_pointer)
        vertice_list = vertice_list + [anotherVertice]
        vertice_pointer = anotherVertice
    return vertice_list


def get_element_frequency(myList):
    each_freq = {}
    for i in range(len(myList)):
        this_item = myList[i]
        each_freq.setdefault(this_item, 0)
        each_freq[this_item] = each_freq[this_item] + 1
    return each_freq


def get_non_dangles_id(o_list, d_list):
    unique_vertices_freq = get_element_frequency(o_list + d_list)
    not_dangles_id = [i for i, x in enumerate(o_list) if (unique_vertices_freq[o_list[i]] > 1) and (unique_vertices_freq[d_list[i]] > 1)]
    return not_dangles_id


def delete_short_roads(roads_single, threshold, myPrecision):
    def lineStringLength(myPointList):
        def myDist(p1, p2):
            return np.sqrt((p1[0] - p2[0]) * (p1[0] - p2[0]) + (p1[1] - p2[1]) * (p1[1] - p2[1]))

        all_len = [myDist(myPointList[i-1], myPointList[i]) for i, x in enumerate(myPointList[1:])]
        total = sum(all_len)
        return total

    def lineString2Tuples(myLine, myPrecision):
        newPointList = [myLine[0], myLine[-1]]
        newPointList = [(round(newPointList[0][0], myPrecision), round(newPointList[0][1], myPrecision)),
                         (round(newPointList[1][0], myPrecision), round(newPointList[1][1], myPrecision))]
        return newPointList

    def get_centroid(all_centroids, mypoint):
        this_root = UFTree.ancestor[mypoint]
        this_centroid = all_centroids[this_root]
        return this_centroid

    too_shorts = [lineString2Tuples(x, myPrecision) for x in roads_single if lineStringLength(x)<threshold]   # Select all too-short roads
    other_roads = [x for x in roads_single if lineStringLength(x)>=threshold]  # Other roads

    UFTree = union_find_tree()
    for i in range(len(too_shorts)):
        UFTree.union(too_shorts[i])
    all_roots = UFTree.find_all_roots()
    all_roots_descendants = {}
    all_roots_centroid = {}
    for i in range(len(all_roots)):
        this_root = all_roots[i]
        all_roots_descendants[this_root] = UFTree.find_all_descendants(this_root, this_root)
        all_roots_descendants[this_root] = all_roots_descendants[this_root] + [this_root]
        all_roots_centroid[this_root] = np.array(all_roots_descendants[this_root]).mean(axis=0)
    for i in range(len(other_roads)):
        this_point = other_roads[i][0]
        this_point = tuple([round(this_point[0], myPrecision), round(this_point[1], myPrecision)])
        if UFTree.myTree.get(this_point) is not None:
            other_roads[i][0] = get_centroid(all_roots_centroid, this_point)

        this_point = other_roads[i][-1]
        this_point = tuple([round(this_point[0], myPrecision), round(this_point[1], myPrecision)])
        if UFTree.myTree.get(this_point) is not None:
            other_roads[i][-1] = get_centroid(all_roots_centroid, this_point)
    other_roads = np.array(other_roads)
    return other_roads


def calculate_running_time(start_time):
    end_time = time()
    total_time = end_time - start_time
    minutes = int(total_time // 60)
    seconds = total_time - 60 * minutes
    seconds = round(seconds, 1)
    print("Running time: {0} minute(s) {1} second(s)".format(minutes, seconds))
    print("")


def create_grids(leftX, rightX, topY, bottomY, myRoads):
    def judge_top_bottom(midY_coord, myLine):
        y1 = myLine.bounds[1]
        y2 = myLine.bounds[3]
        if (y1 >= midY_coord):
            return 1
        elif (y2 <= midY_coord):
            return 0
        else:
            return -1

    def judge_left_right(midX_coord, myLine):
        x1 = myLine.bounds[0]
        x2 = myLine.bounds[2]
        if (x1 >= midX_coord):
            return 1
        elif (x2 <= midX_coord):
            return 0
        else:
            return -1

    global all_grids
    global dist
    if (leftX + 1 == rightX) and (bottomY + 1 == topY):
        all_grids[leftX, bottomY].setRoadAndBuffer(myRoads, dist)
    elif (leftX + 1 == rightX):
        midY = (topY+bottomY) // 2
        leftX_coord = all_grids[leftX, bottomY].bottomLeft[0]
        rightX_coord = all_grids[leftX, bottomY].topRight[0]
        midY_coord = all_grids[leftX, midY].bottomLeft[1]
        hline = LineString([[leftX_coord, midY_coord], [rightX_coord, midY_coord]])
        top_part = []
        bottom_part = []
        for i in range(len(myRoads)):
            this_road = myRoads[i]
            topOrBottom = judge_top_bottom(midY_coord, this_road)
            if topOrBottom == 1:
                top_part.append(this_road)
            elif topOrBottom == 0:
                bottom_part.append(this_road)
            else:
                temp = list(split(this_road, hline))
                for j in range(len(temp)):
                    this_splitted = temp[j]
                    splitted_topOrBottom = judge_top_bottom(midY_coord, this_splitted)
                    if splitted_topOrBottom == 1:
                        top_part.append(this_splitted)
                    else:
                        bottom_part.append(this_splitted)
        create_grids(leftX, rightX, midY, bottomY, bottom_part)
        create_grids(leftX, rightX, topY, midY, top_part)
    else:
        midX = (leftX + rightX) // 2
        bottomY_coord = all_grids[leftX, bottomY].bottomLeft[1]
        topY_coord = all_grids[leftX, topY - 1].topRight[1]
        midX_coord = all_grids[midX, bottomY].bottomLeft[0]
        vline = LineString([[midX_coord, bottomY_coord], [midX_coord, topY_coord]])
        left_part = []
        right_part = []
        for i in range(len(myRoads)):
            this_road = myRoads[i]
            leftOrRight = judge_left_right(midX_coord, this_road)
            if leftOrRight == 1:
                right_part.append(this_road)
            elif leftOrRight == 0:
                left_part.append(this_road)
            else:
                temp = list(split(this_road, vline))
                for j in range(len(temp)):
                    this_splitted = temp[j]
                    splitted_leftOrRight = judge_left_right(midX_coord, this_splitted)
                    if splitted_leftOrRight == 1:
                        right_part.append(this_splitted)
                    else:
                        left_part.append(this_splitted)
        create_grids(leftX, midX, topY, bottomY, left_part)
        create_grids(midX, rightX, topY, bottomY, right_part)


def getNeighbourBuffer(x, y, grid_num_x, grid_num_y):
    if (x < 0) or (x >= grid_num_x) or (y < 0) or (y >= grid_num_y):
        return None
    else:
        return all_grids[x, y].buffer


def union_all_grids(all_grids, left, right, bottom, top):
    all_buffer = [x.bufferUnionTrimmed for x in all_grids.flat if (x.bufferUnionTrimmed is not None)]
    all_buffer = GeoDataFrame(geometry=all_buffer)
    all_buffer["id"] = 0
    whole_buffer = all_buffer.dissolve(by='id')
    return whole_buffer.geometry[0]


def judge_colinearity(myPointList):
    def get_angle(p1, p2):
        if (abs(p1[0] - p2[0]) < 0.01):
            return 90
        else:
            return 180/np.pi*np.arctan((p1[1] - p2[1]) / (p1[0] - p2[0]))

    colinear = True
    if len(myPointList)>2:
        head_angle = get_angle(myPointList[0], myPointList[1])
        for i in range(2, len(myPointList)):
            this_angle = get_angle(myPointList[i-1], myPointList[i])
            if (abs(this_angle - head_angle) >= 1):
                colinear = False
            if not colinear:
                break
    return colinear


def judge_same_point(p1, p2, myPrecision):
    if (abs(p1[0]-p2[0])<myPrecision) and (abs(p1[1]-p2[1])<myPrecision):
        return True
    else:
        return False



##### Program starts #####
# df = read_file(file_path)

from pandas import concat
file_path = r'D:\实验室\Data\42城市道路划分'
outputPath = r'D:\实验室\Data\42城市道路划分\outputFile'
files = os.listdir(file_path)
for file in files:
    if file.endswith('.shp'):
        if not os.path.isdir(file):
            this_path = os.path.join(file_path, file)
            export_path = os.path.join(outputPath, file)
            if not os.path.isfile(export_path):
                start_time = time()
                df = read_file(this_path)
                df.crs = {"init": "epsg:4326"}
                df = df.to_crs({"init": "epsg:32650"})
                # levels = ['城市高速路', '高速公路', '国道', '省道', '县道', '乡镇村道路']
                # # levels = ['高速公路', '国道', '省道', '县道', '乡镇村道路']
                # df = GeoDataFrame()
                # for i in range(len(levels)):
                #     this_path = file_path + r'\吉林省_' + levels[i] + '.geojson'
                #     newdf = read_file(this_path)
                #     newdf.crs = {"init": "epsg:4326"}
                #     newdf = newdf.to_crs({"init": "epsg:32650"})
                #     df = concat([df, newdf], ignore_index=True)
                simplified_former_road_list = list(df.geometry)
                print("Finish reading file:{0}...".format(file))
                calculate_running_time(start_time)

                ##### Make grids for the road network, and the buffer #####
                all_bounding_boxes = df.bounds
                xmin, ymin, xmax, ymax = min(all_bounding_boxes["minx"]), min(all_bounding_boxes["miny"]), \
                                         max(all_bounding_boxes["maxx"]), max(all_bounding_boxes["maxy"]),
                grid_num_x = round((xmax-xmin) // grid_size)
                if (grid_num_x * grid_size < xmax-xmin):
                    grid_num_x += 1
                grid_num_y = round((ymax-ymin) // grid_size)
                if (grid_num_y * grid_size < ymax-ymin):
                    grid_num_y += 1

                all_grids = np.empty((grid_num_x, grid_num_y), dtype=object)
                for i in range(grid_num_x):
                    for j in range(grid_num_y):
                        all_grids[i, j] = Grid(xmin + grid_size*i, ymin + grid_size*j, xmin + grid_size*(i+1), ymin + grid_size*(j+1))
                create_grids(0, grid_num_x, grid_num_y, 0, simplified_former_road_list)
                print("Finish creating grids...")
                calculate_running_time(start_time)

                next_step = [[1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1]]
                for i in range(all_grids.shape[0]):
                    for j in range(all_grids.shape[1]):
                        bufferList = [getNeighbourBuffer(i+x[0], j+x[1], grid_num_x, grid_num_y) for x in next_step]
                        bufferList = [x for x in bufferList if x is not None]
                        all_grids[i, j].setBufferUnion(bufferList)
                print("Finish making buffer for roads in each grid...")
                calculate_running_time(start_time)

                df_buffer = union_all_grids(all_grids, 0, grid_num_x, 0, grid_num_y)
                if type(df_buffer) == MultiPolygon:
                    buffers = [x for x in df_buffer]
                else:
                    buffers = [df_buffer]
                print('Finish buffering...')
                calculate_running_time(start_time)

                # start_time = time()
                all_points = polygons_to_point_series(buffers, point_dist)
                print("Finish interpolating points on the buffer polygon...")
                calculate_running_time(start_time)

                # Create the Voronoi diagram
                vor = Voronoi(all_points)
                all_vertices = vor.vertices
                print("Finish creating Thiessen Polygon...")
                calculate_running_time(start_time)

                # Filter ridges
                ridges_on_buffer = filter_ridges_inside_buffer(all_grids, vor, xmin, ymin, xmax, ymax, grid_size)
                print("Finish filtering ridges...")
                calculate_running_time(start_time)

                # Clean cul-de-sacs among the ridges
                o_list = [x[0] for x in ridges_on_buffer]
                d_list = [x[1] for x in ridges_on_buffer]
                non_dangles_id = get_non_dangles_id(o_list, d_list)
                ridges_on_buffer = [ridges_on_buffer[i] for i in non_dangles_id]
                print("Finish deleting dangles...")
                calculate_running_time(start_time)

                # Group roads into sections
                edge_dict = create_vertice_dict(ridges_on_buffer)
                edge_dict_used = deepcopy(edge_dict)
                vertice_degree = get_element_frequency([x[0] for x in ridges_on_buffer] + [x[1] for x in ridges_on_buffer])
                crosspoints = [x for x, y in zip(edge_dict_used.keys(), edge_dict_used.values()) if len(y) > 2]
                allRoadList = []
                for i in range(len(crosspoints)):
                    this_crosspoint = crosspoints[i]
                    this_verticeList = edge_dict_used[this_crosspoint].copy()
                    for another_vertice in this_verticeList:
                        if another_vertice in edge_dict_used[this_crosspoint]:   # This is to prevent the case that two of its edges are in the same loop
                            edge_dict_used[this_crosspoint].remove(another_vertice)
                            edge_dict_used[another_vertice].remove(this_crosspoint)
                            new_road = search_seperated_roads(another_vertice)
                            new_road = [this_crosspoint] + new_road
                            allRoadList.append(new_road)
                print("Finish seperating roads...")
                calculate_running_time(start_time)

                # Convert ridge list to road list
                for i in range(len(allRoadList)):
                    this_roadlist = allRoadList[i]
                    this_roadlist = [all_vertices[x] for x in this_roadlist]
                    allRoadList[i] = this_roadlist

                # Simplify roads
                roads_seperated = [np.asarray(x) for x in allRoadList]
                roads_single = [rdp(x, epsilon=rdp_eps) for x in roads_seperated]
                print("Finish simplifying roads...")
                calculate_running_time(start_time)

                # Clean too-short roads
                final_roads = delete_short_roads(roads_single, threshold, margin_pos)
                print("Finish cleaning short roads...")
                calculate_running_time(start_time)

                # Delete dangles again
                o_list = [tuple([round(x[0][0], margin_pos), round(x[0][1], margin_pos)]) for x in final_roads]
                d_list = [tuple([round(x[-1][0], margin_pos), round(x[-1][1], margin_pos)]) for x in final_roads]
                non_dangles_id = get_non_dangles_id(o_list, d_list)
                final_roads = [final_roads[i] for i in non_dangles_id if (len(final_roads[i]) == 2) or
                               (not (judge_same_point(final_roads[i][0], final_roads[i][-1], 0.01) and
                               judge_colinearity(final_roads[i])))]
                print("Finish deleting dangles again...")
                calculate_running_time(start_time)

                # Output
                final_roads = [LineString(x) for x in final_roads]
                final_roads = GeoDataFrame(geometry=final_roads)
                final_roads.crs = {"init": "epsg:32650"}
                final_roads.to_file(export_path, driver='ESRI Shapefile')
                print("Finish!")
                calculate_running_time(start_time)

