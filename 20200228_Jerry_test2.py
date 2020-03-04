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


import io
import json
import hashlib
import math
import requests
import time
import re
import datetime as dt
import os
import logging as lg
from collections import OrderedDict
from dateutil import parser as date_parser
from osmnx.errors import *
from osmnx.utils import make_str, log

from osmnx import settings
from osmnx.downloader import get_from_cache, get_http_headers, get_pause_duration, save_to_cache

import geopandas as gpd
import logging as lg
import math
import networkx as nx
import numpy as np
import pandas as pd
import time

from itertools import groupby
from shapely.geometry import LineString
from shapely.geometry import MultiPolygon
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.ops import unary_union

from osmnx import settings
from osmnx.projection import project_geometry
from osmnx.projection import project_gdf
from osmnx.simplify import simplify_graph
from osmnx.utils import make_str, log
from osmnx.geo_utils import get_largest_component
from osmnx.utils import great_circle_vec
from osmnx.geo_utils import get_nearest_node
from osmnx.geo_utils import geocode
from osmnx.geo_utils import count_streets_per_node
from osmnx.geo_utils import overpass_json_from_file
from osmnx.downloader import osm_polygon_download
from osmnx.downloader import get_osm_filter
from osmnx.downloader import overpass_request
from osmnx.errors import *
from osmnx.core import consolidate_subdivide_geometry, get_polygons_coordinates

import pprint


#matplotlib inline

old_market = (1.4052585, 103.9023302)

def create_graph(response_jsons, name='unnamed', retain_all=False, bidirectional=False):
    """
    Create a networkx graph from Overpass API HTTP response objects.

    Parameters
    ----------
    response_jsons : list
        list of dicts of JSON responses from from the Overpass API
    name : string
        the name of the graph
    retain_all : bool
        if True, return the entire graph even if it is not connected
    bidirectional : bool
        if True, create bidirectional edges for one-way streets

    Returns
    -------
    networkx multidigraph
    """

    log('Creating networkx graph from downloaded OSM data...')
    start_time = time.time()

    # make sure we got data back from the server requests
    elements = []
    # for response_json in response_jsons:
        #elements.extend(response_json['elements'])
    elements.extend(response_jsons['elements'])
    if len(elements) < 1:
        raise EmptyOverpassResponse('There are no data elements in the response JSON objects')

    # create the graph as a MultiDiGraph and set the original CRS to default_crs
    G = nx.MultiDiGraph(name=name, crs=settings.default_crs)

    # extract nodes and paths from the downloaded osm data
    nodes = {}
    paths = {}
    # for osm_data in response_jsons:
    #     nodes_temp, paths_temp = parse_osm_nodes_paths(osm_data)
    #     for key, value in nodes_temp.items():
    #         nodes[key] = value
    #     for key, value in paths_temp.items():
    #         paths[key] = value
    nodes_temp, paths_temp = ox.parse_osm_nodes_paths(response_jsons)
    for key, value in nodes_temp.items():
        nodes[key] = value
    for key, value in paths_temp.items():
        paths[key] = value
        
    # add each osm node to the graph
    for node, data in nodes.items():
        G.add_node(node, **data)

    # add each osm way (aka, path) to the graph
    G = ox.add_paths(G, paths, bidirectional=bidirectional)

    # retain only the largest connected component, if caller did not
    # set retain_all=True
    if not retain_all:
        G = get_largest_component(G)

    log('Created graph with {:,} nodes and {:,} edges in {:,.2f} seconds'.format(len(list(G.nodes())), len(list(G.edges())), time.time()-start_time))

    # add length (great circle distance between nodes) attribute to each edge to
    # use as weight
    if len(G.edges) > 0:
        G = ox.add_edge_lengths(G)

    return G

# def overpass_request(data, pause_duration=None, timeout=180, error_pause_duration=None):
#     """
#     Send a request to the Overpass API via HTTP POST and return the JSON
#     response.
#     Parameters
#     ----------
#     data : dict or OrderedDict
#         key-value pairs of parameters to post to the API
#     pause_duration : int
#         how long to pause in seconds before requests, if None, will query API
#         status endpoint to find when next slot is available
#     timeout : int
#         the timeout interval for the requests library
#     error_pause_duration : int
#         how long to pause in seconds before re-trying requests if error
#     Returns
#     -------
#     dict
#     """

#     # define the Overpass API URL, then construct a GET-style URL as a string to
#     # hash to look up/save to cache
#     url = settings.overpass_endpoint.rstrip('/') + '/interpreter'
#     prepared_url = requests.Request('GET', url, params=data).prepare().url
#     cached_response_json = get_from_cache(prepared_url)

#     if cached_response_json is not None:
#         # found this request in the cache, just return it instead of making a
#         # new HTTP call
#         return cached_response_json

#     else:
#         # if this URL is not already in the cache, pause, then request it
#         if pause_duration is None:
#             this_pause_duration = get_pause_duration()
#         log('Pausing {:,.2f} seconds before making API POST request'.format(this_pause_duration))
#         time.sleep(this_pause_duration)
#         start_time = time.time()
#         log('Posting to {} with timeout={}, "{}"'.format(url, timeout, data))
#         response = requests.post(url, data=data, timeout=timeout, headers=get_http_headers())

#         # get the response size and the domain, log result
#         size_kb = len(response.content) / 1000.
#         domain = re.findall(r'(?s)//(.*?)/', url)[0]
#         log('Downloaded {:,.1f}KB from {} in {:,.2f} seconds'.format(size_kb, domain, time.time() - start_time))

#         try:
#             response_json = response.json()
#             if 'remark' in response_json:
#                 log('Server remark: "{}"'.format(response_json['remark'], level=lg.WARNING))
#             save_to_cache(prepared_url, response_json)
#         except Exception:
#             # 429 is 'too many requests' and 504 is 'gateway timeout' from server
#             # overload - handle these errors by recursively calling
#             # overpass_request until we get a valid response
#             if response.status_code in [429, 504]:
#                 # pause for error_pause_duration seconds before re-trying request
#                 if error_pause_duration is None:
#                     error_pause_duration = get_pause_duration()
#                 log(
#                     'Server at {} returned status code {} and no JSON data. Re-trying request in {:.2f} seconds.'.format(
#                         domain,
#                         response.status_code,
#                         error_pause_duration),
#                     level=lg.WARNING)
#                 time.sleep(error_pause_duration)
#                 response_json = overpass_request(data=data, pause_duration=pause_duration, timeout=timeout)

#             # else, this was an unhandled status_code, throw an exception
#             else:
#                 log('Server at {} returned status code {} and no JSON data'.format(domain, response.status_code),
#                     level=lg.ERROR)
#                 raise Exception(
#                     'Server returned no JSON data.\n{} {}\n{}'.format(response, response.reason, response.text))

#         return response_json
    

query_str = '[out:json][timeout:180];(relation["type"="route"]["route"="bus"](1.385700,103.887300,1.422000,103.925900);>;);out;'
response_json = ox.overpass_request(data={'data':query_str}, timeout=180)

# for x in response_json:
#     print(x)

#print(response_json['elements'])

G = ox.create_graph(response_json,name='unnamed')

n, e = ox.graph_to_gdfs(G)

print(n.head())

print(e.head())

n.to_csv("newnew1.csv")

e.to_csv("eeeee2.csv")


#ox.plot_graph(G, fig_height=10, fig_width=10, edge_color="black")



# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(response_json)




# rj = overpass_request('[out:json][timeout:25];(relation["type"="route"]["route"="bus"]({1.3857},{103.8873},{1.4220},{103.9259}););out body;>;out skel qt;')

# print(rj)

#box = (1.4220, 1.3863, 103.9259, 103.8895)

#G = ox.create_poi_gdf("map.geojson")

#G = ox.graph_from_file("map")

# with open("ee.json", "r") as read_file:
#         osm_data = [json.load(read_file)]

# G1 = ox.create_graph(osm_data)

# ox.plot_graph(G1, fig_height=10, fig_width=10, edge_color="black")

# pois = gpd.read_file("busstop.geojson")

# pois['key'] = pois.index

# print(pois.head(5))

# nodes = gpd.read_file('data/sample/nodes/nodes.shp')
# edges = gpd.read_file('data/sample/edges/edges.shp')

# new_nodes, new_edges = connect_poi(pois, nodes, edges, key_col='key', path=None)

# new_nodes.to_csv("teoooo.csv")

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
    # G.graph['crs'] = gdf_nodes.crs(epsg=4326)
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

# G2 = gdfs_to_grapht(new_nodes,new_edges)

# ttn,tte = ox.graph_to_gdfs(G2)

# tte.plot(linewidth=0.8, figsize=(18,10))

# ttn.to_csv("testt2.csv")
# indexNames = ttn[ (ttn['x'] == np.nan) ].index
# ttn.drop(indexNames , inplace=True)

# test = ttn.where(ttn["x"], None) 
# print(test.head())

# ttn = gpd.read_file("ttttn.csv")

# tte = gpd.read_file("tttte.csv")

# G3 = ox.gdfs_to_graph(ttn,tte)

# ttn.to_csv("ttttn.csv")
# tte.to_csv("tttte.csv")
# ox.plot_graph(G3, fig_height=10, fig_width=10, edge_color="black")

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
# new_edges.plot(linewidth=0.8, figsize=(18,10))

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


