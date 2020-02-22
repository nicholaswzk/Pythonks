import numpy as np
import osmnx as ox
import networkx as nx
import MyQueue

#matplotlib inline

#! -------------------------------------- Defaults -----------------------------------
old_market = (1.4052, 103.9024)
G = ox.graph_from_point(old_market, distance=300, truncate_by_edge=True)# quick plot
#! -------------------------------------- Defaults -----------------------------------

#! --------------------------------------- GET Random destination and source ---------------------------------------
#TODO: o = np.random.choice(G.nodes)
#TODO: d = np.random.choice(G.nodes)
#TODO: print("test: ", o, "testt: ", d)
#! --------------------------------------- GET Random destination and source ---------------------------------------

#! --------------------------------------- Testing Phrase 2 ---------------------------------------


#TODO -------------------------- Working A* Algo --------------------------
c = it.count()
pq = MyQueue.PriorityQ()
#! Format is (Unique ID, Source, Distance, Parent)
#! next(c) is to create a uniqueness for each obj in the Priority Q
#! Source is the starting node
#! Distance for starting will be zero
#! Parent, starting does not have any parent thus None is placed
pq.push(next(c), 4598672210, 0, None)

#! Used nodes or nodes that have been stepped thru
used = {}

#! Starting of A* Algo
while pq.getSize() > 0:
    #! Get the Priority obj within the priority Q. Priority by Distance
    _, curN, dis, p = pq.pop()
    #! When path is found. Below is static, if dynamic can put curN == endN
    if curN == 4004983342:
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
        print(finalpath)
        break
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
        ndis = dis + etc.get('length', 1)
        pq.push(next(c), nei, ndis, curN)
#TODO -------------------------- Working A* Algo --------------------------



#* ----------------- Checking for correctness of algo -----------------
#TODO(Checking if correct): route = nx.astar_path(nx.DiGraph(G), 4598672210, 4004983342)

#ox.plot_graph_route(G, finalpath, fig_height=10, fig_width=10)
#* ----------------- Checking for correctness of algo -----------------


#! --------------------------------------- Testing Phrase 2 ---------------------------------------


#! --------------------------------------- Testing Phrase 1 ---------------------------------------
# t = (1.3984, 103.9072)
# G = ox.graph_from_point(t, distance=1200)

# o = list(G.nodes())[0]
# d = list(G.nodes())[20]

# nextlevel={o:1}

# paths={o:[o]}

# print(nextlevel)

# print(G[o])

# for v in nextlevel:
#     print(v, " test")
#     for w in G[v]:
#         print(w, " test2")

# print(paths)

# print(o, d)


# n, e = ox.graph_to_gdfs(G)

# print(n.head())

# print(e.head())

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
#! --------------------------------------- Testing Phrase 1 ---------------------------------------