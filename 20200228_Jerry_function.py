import numpy as np
import osmnx as ox
import networkx as nx
import math
import matplotlib.pyplot as plt
import pandas as pd
import MyQueue
import itertools as it
import geopandas as gpd

#matplotlib inline

old_market = (1.4052585, 103.9023302)

box = (1.4220, 1.3863, 103.9259, 103.8895)

G = ox.create_poi_gdf("map.geojson")

#G = ox.graph_from_file("map")

#G = ox.graph_from_bbox(1.42103880000, 1.39289490000, 103.92311100000, 103.89616010000, simplify=True, retain_all=False)# quick plot

#G = ox.graph_from_point(old_market, distance=2500, truncate_by_edge=True)# quick plot

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
            #TODO(DEBUG):  print(nei, etc)
            #TODO(DEBUG):   print(curN, nei)
            if nei in used:
                continue
            #! 'length' can be any numeric data in etc
            ndis = dis + etc[0].get("length")
            f = heuristic(nei,endN) + ndis
            pq.push(f,next(c), nei, ndis, curN)
    return -1


n, e = ox.graph_to_gdfs(G)

print(n.head())

print(e.head())

n.to_csv("nodes.csv")

e.to_csv("e.csv")

# countries_gdf = gpd.read_file("punggol.geojson")

#countries_gdf.to_csv("test.csv")

# test1xy = (1.404062, 103.904901)

# test2xy = (1.393783, 103.91052)

# t1 = ox.get_nearest_node(G, test1xy)

# t2 = ox.get_nearest_node(G, test2xy)

# print(astar(t1,t2))


