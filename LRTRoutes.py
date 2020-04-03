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
    """To Select the nearest LRT station that is closest to the start point and end point"""
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
            currStation = getDirectDistance(G, i, EndN)
            if currStation < currentNearestHn:
                currentNearestHn = currStation
                NearestStation = i
        return NearestStation
    else:
        for i in StationWest:
            currStation = getDirectDistance(G, i, EndN)
            if currStation < currentNearestHn:
                currentNearestHn = currStation
                NearestStation = i
        return NearestStation


def LRTPathFinder(G, StartPt, EndStation):
    """To path find the StartStation to the Endstation, this will return a path or array of node to node edge function.
    In order for the Function to return the path, the path will find until the node is 50 metres from the endStation
    This Function uses Breadth-First Search but of queue, it utilises 2 arrays as there is only 2 direction that LRT can go"""
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
            for nei, etc in G[LRTRoute1[-1]].items():
                if(nei not in LRTRoute1):
                    LRTRoute1.append(nei)
                    if (getDirectDistance(G, EndStation, nei) < 0.05):
                        return LRTRoute1
            for i in G[LRTRoute2[-1]]:
                if (i not in LRTRoute2):
                    LRTRoute2.append(i)
                    if (getDirectDistance(G, EndStation, i) < 0.05):
                        return LRTRoute2


def getDirectDistance(G, Node1, Node2):
    """This function is utilised to find the direct distance in KILOMETRES between 2 nodes"""
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
    """This function is utilised to find the direct distance in Kilometres between 2 lat lng"""
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
    return R * c  # if less than 0.2 recommend walk


def getClosestStation(G, Node, destination):
    """This function returns the distance between 2 nodes in lat lng units"""
    lat1 = math.radians(G.nodes[Node]['y'])
    lon1 = math.radians(G.nodes[Node]['x'])
    dist = math.sqrt((G.nodes[Node]['x'] - destination[1])
                     ** 2 + (G.nodes[Node]['y'] - destination[0]) ** 2)
    return dist


def LRT(EastLoopG, WestLoopG, StartLatLng, DestLatLng):
    """The main function of LRT returns the array of tuples of linestring, utilsed to draw the routes on the map"""
    destination = DestLatLng
    Startpoint = StartLatLng
    # Determine which loop Start Station is
    t1 = ox.get_nearest_node(EastLoopG, Startpoint)
    t2 = ox.get_nearest_node(WestLoopG, Startpoint)
    WestStartstation = LRTSelector(WestLoopG, t2, 1)
    EastStartStation = LRTSelector(EastLoopG, t1, 0)
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

    WestD = getClosestStation(WestLoopG, WestEndStation, destination)
    EastD = getClosestStation(EastLoopG, EastEndStation, destination)
    if (WestD > EastD):
        LoopFlag = "East"
        EndStation = EastEndStation
    else:
        LoopFlag = "West"
        EndStation = WestEndStation

    if StartStation == EndStation:
        return 0

    finalpath = []
    
    #This if statement is to check whether startstation and End station is in the same loop therefore requiring no change by the user
    if (StartLoopFlag == LoopFlag or StartStation == 6587709456 or EndStation == 6587709456):
        if (LoopFlag == "East"):
            s = LRTPathFinder(EastLoopG, Startpoint, EndStation)
            finalpath.append(ox.node_list_to_coordinate_lines(EastLoopG, s))
            return finalpath
        elif(LoopFlag == "West"):
            s = LRTPathFinder(WestLoopG, Startpoint, EndStation)
            finalpath.append(ox.node_list_to_coordinate_lines(WestLoopG, s))
            return finalpath
    #If dont exist in same loop of the LRT
    else:
        #If the start is in the East loop and the end station is in the West loop
        if (LoopFlag == "West" and StartLoopFlag == "East"):

            s = LRTPathFinder(EastLoopG, Startpoint, 6587709456)
            finalpath.append(ox.node_list_to_coordinate_lines(EastLoopG, s))

            TempPoint = (WestLoopG.nodes[6587709457]
                         ['y'], WestLoopG.nodes[6587709457]['x'])
            s = LRTPathFinder(WestLoopG, TempPoint, EndStation)
            finalpath.append(ox.node_list_to_coordinate_lines(WestLoopG, s))
            return finalpath
        ##If the start is in the West loop and the end station is in the EAST loop
        elif(LoopFlag == "East" and StartLoopFlag == "West"):

            s = LRTPathFinder(WestLoopG, Startpoint, 6587709456)
            finalpath.append(ox.node_list_to_coordinate_lines(WestLoopG, s))
            TempPoint = (EastLoopG.nodes[6587709456]
                         ['y'], EastLoopG.nodes[6587709456]['x'])
            s = LRTPathFinder(EastLoopG, TempPoint, EndStation)
            finalpath.append(ox.node_list_to_coordinate_lines(EastLoopG, s))
            return finalpath
