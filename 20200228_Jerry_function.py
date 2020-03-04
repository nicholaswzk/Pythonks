import numpy as np
import osmnx as ox
import networkx as nx
import math
import matplotlib.pyplot as plt
import pandas as pd
import MyQueue
import itertools as it
import geopandas as gpd
from toolbox import connect_poi
from geopandas.geodataframe import GeoDataFrame
from geopy.point import Point



# import re
# import time
# import os
# import ast
# import numpy as np
# import pandas as pd
# import geopandas as gpd
# import networkx as nx
# from shapely.geometry import Point
# from shapely.geometry import LineString
# from shapely import wkt
# from xml.etree import ElementTree as etree

#matplotlib inline

old_market = (1.4052585, 103.9023302)

#box = (1.4220, 1.3863, 103.9259, 103.8895)

#G = ox.create_poi_gdf("map.geojson")

#G = ox.graph_from_file("map")

pois = gpd.read_file("busstop.geojson")

pois['key'] = pois.index

print(pois.head(5))

nodes = gpd.read_file('data/sample/nodes/nodes.shp')
edges = gpd.read_file('data/sample/edges/edges.shp')

new_nodes, new_edges = connect_poi(pois, nodes, edges, key_col='key', path=None)

    

#ox.plot_graph(G2, fig_height=10, fig_width=10, edge_color="black")

#G = ox.graph_from_bbox(1.42103880000, 1.39289490000, 103.92311100000, 103.89616010000, simplify=True, retain_all=False)# quick plot

# G = ox.graph_from_point(old_market, distance=2500, truncate_by_edge=True)# quick plot

# node, edge = ox.graph_to_gdfs(G)




def gdfs_to_grapht(gdf_nodes, gdf_edges):
    """
    Convert node and edge GeoDataFrames into a graph
    Parameters
    ----------
    gdf_nodes : GeoDataFrame
    gdf_edges : GeoDataFrame
    Returns
    -------
    networkx multidigraph
    """

    G = nx.MultiDiGraph()
    G.graph['crs'] = gdf_nodes.crs
    print(gdf_nodes.crs)
    #print(gdf_nodes.gdf_name)
    G.graph['name'] = "unnamed"

    # add the nodes and their attributes to the graph
    G.add_nodes_from(gdf_nodes.index)
    attributes = gdf_nodes.to_dict()
    for attribute_name in gdf_nodes.columns:
        # only add this attribute to nodes which have a non-null value for it
        attribute_values = {k:v for k, v in attributes[attribute_name].items() if pd.notnull(v)}
        nx.set_node_attributes(G, name=attribute_name, values=attribute_values)

    # add the edges and attributes that are not u, v, key (as they're added
    # separately) or null
    for _, row in gdf_edges.iterrows():
        attrs = {}
        for label, value in row.iteritems():
            if (label not in ['from', 'to', 'key']) and (isinstance(value, list) or pd.notnull(value)):
                attrs[label] = value
        G.add_edge(row['from'], row['to'], key=row['key'], **attrs)

    return G

#G2 = gdfs_to_grapht(node, edge)

G2 = gdfs_to_grapht(new_nodes,new_edges)

ttn,tte = ox.graph_to_gdfs(G2)

ttn.to_csv("testt2.csv")
# delete all rows with column 'Age' has value 30 to 40 
indexNames = ttn[ (ttn['x'] == 'None') ].index
ttn.drop(indexNames , inplace=True)

ttn.to_csv("testttttt.csv")

# ttn = gpd.read_file("ttttn.csv")

# tte = gpd.read_file("tttte.csv")

G3 = ox.gdfs_to_graph(ttn,tte)

# ttn.to_csv("ttttn.csv")
# tte.to_csv("tttte.csv")
ox.plot_graph(G3, fig_height=10, fig_width=10, edge_color="black")

def heuristic(curnode, endnode):
   return math.sqrt((G.nodes[endnode].get('x') - G.nodes[curnode].get('x')) ** 2 + (G.nodes[endnode].get('y') - G.nodes[curnode].get('y')) ** 2)

def astar(startN, endN):
    c = it.count()
    pq = MyQueue.PriorityQ()
    #! Format is (Unique ID, Source, Distance, Parent)
    #! next(c) is to create a uniqueness for each obj in the Priority Q
    #! Source is the starting node
    #! Distance for starting will be zero
    #! Parent, starting does not have any parent thus None is placed
    pq.push(0, next(c), startN, 0.0, None)

    #! Used nodes or nodes that have been stepped thru
    used = {}

    #! Starting of A* Algo
    while pq.getSize() > 0:
        #! Get the Priority obj within the priority Q. Priority by Distance
        _, __, curN, dis, p = pq.pop()
        #! When path is found. Below is static, if dynamic can put curN == endN
        if curN == endN:
            #! Building the path, end node will be appended first, then slowly search for the parent from the used dict -
            #! and the parent node will be appended until the start node. Then reverse the array it will show the path from start to end.
            #! Lastly it will be break out of this while loop
            finalpath = []
            finalpath.append(curN)
            n = p
            while n is not None:
                finalpath.append(n)
                n = used[n]
            finalpath = finalpath[::-1]
            return (finalpath, dis)
        #! to make it efficient and prevent endless loop, if the current Node is found within used nodes, -
        #! it will just skip to the next Queue object
        if curN in used:
            continue
        #! Adding current node into the used dict and linked it with the parent node.
        used[curN] = p
        #! Searching for the paths
        #? nei (NODE ID) e.g
        #? 5103941180
        ###################
        #? etc (dict) e.g
        #? {'osmid': 35091912, 'oneway': True, 'lanes': '2', 'name': 'Punggol Place', 'highway': 'residential', 'maxspeed': '40', 'length': 25.879} 1
        #! ndis is new distance
        for nei, etc in G[curN].items():
            # TODO print(nei, etc)
            # TODO print(curN, nei)
            if nei in used:
                continue
            #! 'length' can be any numeric data in etc
            ndis = dis + etc[0].get("length")
            f = heuristic(nei,endN) + ndis
            pq.push(f,next(c), nei, ndis, curN)
    return -1

# pois = gpd.read_file("busstop.geojson")

# print(pois.head())

# nodes = gpd.read_file('data/sample/nodes/nodes.shp')
# edges = gpd.read_file('data/sample/edges/edges.shp')

# new_nodes, new_edges = connect_poi(pois, nodes, edges, key_col='id', path=None)

# poi_links = new_edges[new_edges['highway'] == 'poi']
# ax = edges.plot(linewidth=0.8, figsize=(18,10), label='Original Road Edges')
# poi_links.plot(color='indianred', linewidth=2, ax=ax, label='New Connection Edges')
# pois.plot(color='indianred', marker='.', markersize=200, ax=ax, label='POI')
# ax.legend(loc=2, fontsize=18)
# ax.set_title('The integrated network of supermarkets and road network at Toa Payoh', fontsize=22)

# new_nodes.to_csv("n1.csv")
# new_edges.to_csv("e1.csv")
#new_nodes, new_edges = connect_poi(pois, nodes, edges, key_col='key', path=None)


#ox.plot_graph(G, fig_height=10, fig_width=10, edge_color="black")

#! ---------------------------Testing---------------------------
# n, e = ox.graph_to_gdfs(G)

#ox.save_graph_shapefile(G, filename='sample', folder=None, encoding='utf-8')

# print(n.head())

# print(e.head())

# n.to_csv("nodes.csv")

# e.to_csv("e.csv")

# countries_gdf = gpd.read_file("punggol.geojson")

#countries_gdf.to_csv("test.csv")

# test1xy = (1.404062, 103.904901)

# test2xy = (1.393783, 103.91052)

# t1 = ox.get_nearest_node(G, test1xy)

# t2 = ox.get_nearest_node(G, test2xy)

# print(astar(t1,t2))

#! ---------------------------Testing---------------------------


