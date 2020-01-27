import numpy as np
import osmnx as ox
import networkx as nx

t = (1.3984, 103.9072)
G = ox.graph_from_point(t, distance=1200)

o = list(G.nodes())[0]
d = list(G.nodes())[20]

nextlevel={o:1}

paths={o:[o]}

print(nextlevel)

print(G[o])

for v in nextlevel:
    print(v, " test")
    for w in G[v]:
        print(w, " test2")

print(paths)

print(o, d)


n, e = ox.graph_to_gdfs(G)

print(n.head())

print(e.head())

#n.to_csv("nodes.csv")

#e.to_csv("e.csv")

#ox.plot_graph(G, fig_height=10, fig_width=10, edge_color="black")

# print(np.random.choice(G.nodes))

# kk = np.random.choice(G.nodes)
# print(G.nodes[kk]['y'][1])
#xx = (G.nodes[kk]['y'], G.nodes[kk]['x'])

#print(ox.get_node(xx))

#route = nx.shortest_path(G, np.random.choice(G.nodes), np.random.choice(G.nodes))


#ox.plot_graph_route(G, route, fig_height=10, fig_width=10)