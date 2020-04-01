import networkx as nx
import osmnx as ox
import math


def get_node(element):
    useful_tags_node = ['ref', 'highway', 'route_ref']
    node = {}
    node['y'] = element['lat']
    node['x'] = element['lon']
    node['osmid'] = element['id']

    if 'tags' in element:
        for useful_tag in useful_tags_node:
            if useful_tag in element['tags']:
                node[useful_tag] = element['tags'][useful_tag]
    return node


def parse_osm_nodes_paths(osm_data):

    nodes = {}
    paths = {}
    for element in osm_data['elements']:
        if element['type'] == 'node':
            key = element['id']
            nodes[key] = get_node(element)
        elif element['type'] == 'way':  # osm calls network paths 'ways'
            key = element['id']
            paths[key] = ox.get_path(element)

    return nodes, paths


def create_graph(response_jsons, name='unnamed', retain_all=True, bidirectional=False):
    # make sure we got data back from the server requests
    elements = []

    elements.extend(response_jsons['elements'])
    if len(elements) < 1:
        raise ox.EmptyOverpassResponse(
            'There are no data elements in the response JSON objects')

    # create the graph as a MultiDiGraph and set the original CRS to default_crs
    G = nx.MultiDiGraph(name=name, crs=ox.settings.default_crs)

    # extract nodes and paths from the downloaded osm data
    nodes = {}
    paths = {}

    nodes_temp, paths_temp = parse_osm_nodes_paths(response_jsons)
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
        G = ox.get_largest_component(G)

    # add length (great circle distance between nodes) attribute to each edge to
    # use as weight
    if len(G.edges) > 0:
        G = ox.add_edge_lengths(G)

    return G


def LRTSelector(G, EndN, Flag):
    # List of Station IDs
    StationsEast = [1840734592, 1840734597, 1840734578,
                    1840734604, 1840734594, 1840734599, 1840734593, 6587709456]
    StationWest = [1840734606, 1840734600, 1840734607,
                   1840734598, 1840734610, 1840734608, 6587709456]
    currentNearestHn = 10000
    NearestStation = 0
    # Get Nearest Station to EndNode
    if (Flag == 0):
        for i in StationsEast:
            # print(i)
            currStation = getDirectDistance(G, i, EndN)
            if currStation < currentNearestHn:
                currentNearestHn = currStation
                NearestStation = i
        return NearestStation
    else:
        for i in StationWest:
            # print(i)
            currStation = getDirectDistance(G, i, EndN)
            if currStation < currentNearestHn:
                currentNearestHn = currStation
                NearestStation = i
        return NearestStation


def LRTPathFinder(G, StartPt, EndStation):
    firstLoop = False

    StartNode = ox.get_nearest_edge(G, StartPt)
    StartNode = StartNode[1]
    LRTRoute1 = []
    LRTRoute1.append(StartNode)
    LRTRoute2 = []
    LRTRoute2.append(StartNode)
    while True:
        if (firstLoop == False):
            for i in G[StartNode]:
                if (len(LRTRoute1) == 1):
                    LRTRoute1.append(i)

                elif(len(LRTRoute2) == 1):
                    LRTRoute2.append(i)

            firstLoop = True
        else:
            # print(LRTRoute1)
            for nei, etc in G[LRTRoute1[-1]].items():
                if(nei not in LRTRoute1):
                    #print("Appending: ", nei)
                    LRTRoute1.append(nei)
                    if (getDirectDistance(G, EndStation, nei) < 0.05):
                        # print("Route1")
                        return LRTRoute1
            for i in G[LRTRoute2[-1]]:
                if (i not in LRTRoute2):
                    LRTRoute2.append(i)
                    if (getDirectDistance(G, EndStation, i) < 0.05):
                        #print("Route 2")
                        return LRTRoute2


def getDirectDistance(G, Node1, Node2):
    R = 6373.0
    lat1 = math.radians(G.nodes[Node1]['y'])
    lon1 = math.radians(G.nodes[Node1]['x'])
    lat2 = math.radians(G.nodes[Node2]['y'])
    lon2 = math.radians(G.nodes[Node2]['x'])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * \
        math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def getDistanceKM(start, end):
    R = 6373.0
    lat1 = math.radians(start[0])
    lon1 = math.radians(start[1])
    lat2 = math.radians(end[0])
    lon2 = math.radians(end[1])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * \
        math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # if less than 0.2 walk


def getClosestStation(G, Node, destination):
    lat1 = math.radians(G.nodes[Node]['y'])
    lon1 = math.radians(G.nodes[Node]['x'])
    dist = math.sqrt((G.nodes[Node]['x'] - destination[1])
                     ** 2 + (G.nodes[Node]['y'] - destination[0]) ** 2)
    return dist


def LRT(EastLoopG, WestLoopG, StartLatLng, DestLatLng):
    # query_str = '[out:json][timeout:180];(relation["network"="Singapore Rail"]["route"="monorail"](1.39905,103.90891,1.40620,103.92164);>;);out;'
    # response_json = ox.overpass_request(data={'data': query_str}, timeout=180)
    # EastLoopG = create_graph(response_json, name='unnamed')

    # query_str = '  [out:json][timeout:180];(relation["network"="Singapore Rail"]["route"="monorail"](1.41195,103.89831,1.41911,103.91103);>;);out;'
    # response_json = ox.overpass_request(data={'data': query_str}, timeout=180)
    # WestLoopG = create_graph(response_json, name='unnamed')

    # query_str = '[out:json][timeout:180];(relation["network"="Singapore Rail"]["route"="monorail"](1.4011,103.8977,1.4154,103.9231);>;);out;'
    # response_json = ox.overpass_request(data={'data': query_str}, timeout=180)
    # CombinedG = create_graph(response_json, name='unnamed')
    #ox.plot_graph(CombinedG, fig_height=10, fig_width=10, edge_color="black")

    print("LRT START == ", StartLatLng)
    print("LRT END == ", DestLatLng)
    destination = DestLatLng
    Startpoint = StartLatLng
    # Determine which loop Start Station is
    t1 = ox.get_nearest_node(EastLoopG, Startpoint)
    t2 = ox.get_nearest_node(WestLoopG, Startpoint)
    WestStartstation = LRTSelector(WestLoopG, t2, 1)
    EastStartStation = LRTSelector(EastLoopG, t1, 0)
    # print(WestStartstation)
    # print(EastStartStation)
    WestD = getClosestStation(WestLoopG, WestStartstation, Startpoint)
    EastD = getClosestStation(EastLoopG, EastStartStation, Startpoint)
    if (WestD > EastD):
        StartLoopFlag = "East"
        StartStation = EastStartStation
    else:
        StartLoopFlag = "West"
        StartStation = WestStartstation
    # Determine which loop Endstation is
    t1 = ox.get_nearest_node(EastLoopG, destination)
    t2 = ox.get_nearest_node(WestLoopG, destination)
    WestEndStation = LRTSelector(WestLoopG, t2, 1)
    EastEndStation = LRTSelector(EastLoopG, t1, 0)
    # print(WestEndStation)
    # print(EastEndStation)
    WestD = getClosestStation(WestLoopG, WestEndStation, destination)
    EastD = getClosestStation(EastLoopG, EastEndStation, destination)
    if (WestD > EastD):
        LoopFlag = "East"
        EndStation = EastEndStation
    else:
        LoopFlag = "West"
        EndStation = WestEndStation
    #print("EndStation is: ", EndStation)
    # print(StartLoopFlag)
    # print(LoopFlag)
    if StartStation == EndStation:
        return 0
        #print("Dont Take LRT Please")
        # exit()
    finalpath = []
    if (StartLoopFlag == LoopFlag or StartStation == 6587709456 or EndStation == 6587709456):
        if (LoopFlag == "East"):
            s = LRTPathFinder(EastLoopG, Startpoint, EndStation)
            finalpath.append(ox.node_list_to_coordinate_lines(EastLoopG, s))
            # print(finalpath)
            # ox.plot.plot_graph_route(EastLoopG,finalpath)
            return finalpath
        elif(LoopFlag == "West"):
            s = LRTPathFinder(WestLoopG, Startpoint, EndStation)
            finalpath.append(ox.node_list_to_coordinate_lines(WestLoopG, s))
            # print(finalpath)
            # ox.plot.plot_graph_route(WestLoopG,finalpath)
            return finalpath
    else:
        if (LoopFlag == "West" and StartLoopFlag == "East"):

            s = LRTPathFinder(EastLoopG, Startpoint, 6587709456)
            finalpath.append(ox.node_list_to_coordinate_lines(EastLoopG, s))
            #ox.plot.plot_graph_route(EastLoopG, s)
            # print(finalpath)

            TempPoint = (WestLoopG.nodes[6587709457]
                         ['y'], WestLoopG.nodes[6587709457]['x'])
            s = LRTPathFinder(WestLoopG, TempPoint, EndStation)
            finalpath.append(ox.node_list_to_coordinate_lines(WestLoopG, s))
            return finalpath
            #ox.plot.plot_graph_route(WestLoopG, s)
            # print(finalpath)

            #ox.plot.plot_graph_route(CombinedG, finalpath)

        elif(LoopFlag == "East" and StartLoopFlag == "West"):

            s = LRTPathFinder(WestLoopG, Startpoint, 6587709456)
            #ox.plot.plot_graph_route(WestLoopG, s)
            finalpath.append(ox.node_list_to_coordinate_lines(WestLoopG, s))
            # print(finalpath)
            TempPoint = (EastLoopG.nodes[6587709456]
                         ['y'], EastLoopG.nodes[6587709456]['x'])
            s = LRTPathFinder(EastLoopG, TempPoint, EndStation)
            finalpath.append(ox.node_list_to_coordinate_lines(EastLoopG, s))
            return finalpath
            #ox.plot.plot_graph_route(EastLoopG, s)
            #print (finalpath)
            #ox.plot.plot_graph_route(CombinedG, finalpath)

    #ConvertedfinalPath = ox.node_list_to_coordinate_lines(CombinedG, finalpath)
    # return ConvertedfinalPath

# destination = (1.40334935, 103.90963629958)
# startpoint = (1.4168814, 103.9066298)
# LRTpath = LRT(EastLoopG,WestLoopG,CombinedG,startpoint,destination)
# print(LRTpath)

# print(s)


#ox.plot_graph(G, fig_height=10, fig_width=10, edge_color="black")

#n, e = ox.graph_to_gdfs(G)

# n.to_csv("LRTNodes.csv")

# e.to_csv("LRTEdges.csv")
