import numpy as np
import osmnx as ox
import networkx as nx
import folium
import matplotlib.pyplot as plt

punggol = (1.3984, 103.9072)
G = ox.graph_from_point(punggol, distance=2000)
mrt = ox.geocode('Punggol, Punggol Central, Punggol, Northeast, 828868, Singapore')
hdb = ox.geocode('Waterway Sunray, 659B, Punggol East, Punggol, Northeast, 822659, Singapore')

mrt_node = ox.get_nearest_node(G,mrt,method='euclidean',return_dist=False)
hdb_node = ox.get_nearest_node(G,hdb,method='euclidean',return_dist=False)
route = nx.shortest_path(G, mrt_node, hdb_node)
fig, ax = ox.plot_graph_route(G, route, fig_height=10, 
                              fig_width=10, 
                              show=False, close=False, 
                              edge_color='black',
                              orig_dest_node_color='green',
                              route_color='green')

ax.scatter(mrt[1], mrt[0], c='red', s=100)
ax.scatter(hdb[1], hdb[0], c='blue', s=100)
plt.show()