from multiprocessing.dummy import shutdown

import numpy as np
import osmnx as ox
import networkx as nx
import myQueue
import itertools as it
import math
import logging
import time
import concurrent.futures
from multiprocessing import Pool
from itertools import product



#! -------------------------------------- Defaults -----------------------------------
mrtstation = (1.4052585, 103.9023302)
G = ox.graph_from_point(mrtstation, distance=3000, truncate_by_edge=True)# quick plot
def heuristic(curnode, endnode):
   return math.sqrt((G.nodes[endnode].get('x') - G.nodes[curnode].get('x')) ** 2 + (G.nodes[endnode].get('y') - G.nodes[curnode].get('y')) ** 2)

def astar(startN, endN):
    c = it.count()
    pq = myQueue.PriorityQ()
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

test1xy = (1.404062, 103.904901)
test2xy = (1.393783, 103.91052)
test3xy = (1.4159537, 103.9021398)
test4xy = (1.4039261, 103.9111051)
t1 = ox.get_nearest_node(G, test1xy)
t2 = ox.get_nearest_node(G, test2xy)
t3 = ox.get_nearest_node(G, test3xy)
t4 = ox.get_nearest_node(G, test4xy)

# t0 = time.process_time()
# print(astar(t1,t2))
# print(astar(t3,t4))
# t1 = time.process_time()
# print("Elapsed time for no threading in seconds:", t1-t0)


#from multiprocessing import Process

if __name__ == '__main__':
    start = time.process_time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(astar, t1,t2)
        f2 = executor.submit(astar, t3,t4)
        print(f1.result())
        print(f2.result())
        print("done")
        executor.shutdown(wait=True)
    end = time.process_time()
    print("Elapsed time for threading in seconds:", end - start)





#processes = []
#processdata = [t1,t2,t3,t4]
 #   for i in range(2):
  #      p = Process(target=astar,args=[processdata[i],])
   #     p.start()
    #    processes.append(p)

 #   for process in processes:
  #      process.join()
