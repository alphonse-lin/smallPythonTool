import networkx as nx
from geopandas import read_file
from shapely.geometry.multilinestring import MultiLineString
import json


def round_tuple(x, digits):
    new_tuple = tuple(round(a, digits) for a in x)
    return new_tuple


def gdf2graph(df):
    o_list = []
    d_list = []
    len_list = []

    for i in range(len(df)):
        this_line = df.loc[i, "geometry"]
        this_len = this_line.length

        first_point = this_line.coords[0]
        last_point = this_line.coords[-1]

        first_point = round_tuple(first_point, 3)
        last_point = round_tuple(last_point, 3)

        o_list.append(first_point)
        d_list.append(last_point)
        len_list.append(this_len)

    edge_list = [(x, y) for x, y in zip(o_list, d_list)]
    G = nx.Graph(edge_list)
    for i in range(len(len_list)):
        G.edges[o_list[i], d_list[i]]["weight"] = len_list[i]
        G.edges[o_list[i], d_list[i]]["id"] = i
    return G


def nodegraph2edgegraph(G):
    H = nx.Graph()
    for node in G.nodes:
        neighbours = list(G.neighbors(node))
        neigh_edges = [(node, x) for x in neighbours]
        neigh_attrs = [G.get_edge_data(x[0], x[1]) for x in neigh_edges]
        for i in range(len(neigh_edges) - 1):
            for j in range(i + 1, len(neigh_edges)):
                new_weight = (neigh_attrs[i]["weight"] + neigh_attrs[j]["weight"]) / 2
                H.add_edge(neigh_attrs[i]["id"], neigh_attrs[j]["id"], weight=new_weight, mynode=node)
    return H


def convertGeometryCoords(gdf, firstEPSG, secondEPSG):
    gdf.crs = {"init": "epsg:" + str(firstEPSG)}
    new_gdf = gdf.to_crs({"init": "epsg:" + str(secondEPSG)})
    return new_gdf


def multiline2Linestring(el):
    if type(el) == MultiLineString:
        temp = [x for x in el]
        return temp[0]
    else:
        return el


if __name__ == '__main__':
    # inputFilePath = r'./originalData/bj_temp.geojson'
    # outputFilePath = r'./originalData/road_BT+CL.geojson'

    inputFilePath = r'E:\OneDrive\Documents\实验室\CAAD\114_temp\008_浩鲸平台开发\最终数据\数据集\new_road.geojson'
    outputFilePath = r'E:\OneDrive\Documents\实验室\CAAD\114_temp\008_浩鲸平台开发\最终数据\数据集\output\road_BT+CL.geojson'

    df = read_file(inputFilePath)
    df = convertGeometryCoords(df, 4326, 32650)
    df.geometry = [multiline2Linestring(x) for x in df.geometry]

    G = gdf2graph(df)
    H = nodegraph2edgegraph(G)
    bet_nodes = nx.betweenness_centrality(H, normalized=True, weight="weight")
    clo_nodes = nx.closeness_centrality(H)

    df["betweenness"] = 0
    df["closeness"] = 0

    for i in range(len(df)):
        if bet_nodes.get(i) is not None:
            df.loc[i, "betweenness"] = bet_nodes[i]
        else:
            df.loc[i, "betweenness"] = -1
        if clo_nodes.get(i) is not None:
            df.loc[i, "closeness"] = clo_nodes[i]
        else:
            df.loc[i, "closeness"] = -1

    df=convertGeometryCoords(df, 32650, 4326)

    df.to_file(outputFilePath, driver='GeoJSON')
