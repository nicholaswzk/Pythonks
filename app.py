from flask import Flask, render_template, request, jsonify
from aStar import routeAstar
from LRTRoutes import LRT,create_graph,getDistanceKM
from Bus.Bus import Busroute
import osmnx as ox
import networkx as nx


app = Flask(__name__)
punggol = (1.4052585, 103.9023302)
#Initialise Walking Graph
G = ox.graph_from_point(punggol, distance=2500, truncate_by_edge=True, network_type="walk")

#Initialise the LRT Graphs
query_str = '[out:json][timeout:180];(relation["network"="Singapore Rail"]["route"="monorail"](1.39905,103.90891,1.40620,103.92164);>;);out;'
response_json = ox.overpass_request(data={'data': query_str}, timeout=180)
EastLoopG = create_graph(response_json, name='unnamed')

query_str = '  [out:json][timeout:180];(relation["network"="Singapore Rail"]["route"="monorail"](1.41195,103.89831,1.41911,103.91103);>;);out;'
response_json = ox.overpass_request(data={'data': query_str}, timeout=180)
WestLoopG = create_graph(response_json, name='unnamed')

#Initialise the Bus Graphs
query_str = '[out:json][timeout:180];(node["highway"="bus_stop"](1.3921,103.8883,1.4207,103.9392);>;);out;'
response_json = ox.overpass_request(data={'data': query_str}, timeout=180)
BusG = create_graph(response_json, name='unnamed')

# convert osm linestrings to correct format
def convertRoute(coords):
    output = []
    try:
        for x in range(len(coords)): # Parent Array
            for i in range(len(coords[x])): # Inner Array
                output.append([coords[x][i][1],coords[x][i][0]])
        return output
    except:
        return -1

def getNearestBusStop(bus_node,bus_node_coord):
    bus_node_id = BusG.nodes[bus_node]['osmid']
    
    query_str = '[out:json][timeout:180];node('+str(bus_node_id)+');node(around:100)[highway=bus_stop];out;'
    response_json = ox.overpass_request(data={'data': query_str}, timeout=180)
    nearbyG = create_graph(response_json, name='unnamed')
    
    nearbyG.remove_node(bus_node_id)
    
    try:
        nearest_node = ox.get_nearest_node(nearbyG,bus_node_coord)
    except:
        print("Error in getting nearest bustop")
        return -1
    
    return nearest_node

def getShortestBusRoute(start,end):
    sCoord = (BusG.nodes[start]['y'],BusG.nodes[start]['x'])
    eCoord = (BusG.nodes[end]['y'],BusG.nodes[end]['x'])
    shortest = 0
    final_output = []
    final_sc = 0
    
    # Scenario 1 : start, end
    try:
        scOne = Busroute(start,end)
        if (len(scOne[1]) != 0):
            shortest = len(scOne[1])
            final_output = scOne
            final_sc = 1
        print("Scenario 1 len: ",len(scOne[1]))
    except:
        pass
    
    # Scenario 2 : start_n, end
    try:
        start2 = getNearestBusStop(start,sCoord)
        scTwo = Busroute(start2,end)
        print("Scenario 2 len: ",len(scTwo[1]))
        if (len(scTwo[1]) < shortest and len(scTwo[1]) != 0):
            shortest = len(scTwo[1])
            final_output = scTwo
            final_sc = 2
    except:
        pass
        
    # Scenario 3 : start, end_n
    try:
        end2 = getNearestBusStop(end,eCoord)
        scThree = Busroute(start,end2)
        print("Scenario 3 len: ",len(scThree[1]))
        if (len(scThree[1]) < shortest and len(scThree[1]) != 0):
            shortest = len(scThree[1])
            final_output = scThree
            final_sc = 3
    except:
        pass
        
    # Scenario 4 : start_n, end_n
    try:
        scFour = Busroute(start2,end2)
        print("Scenario 4 len: ",len(scFour[1]))
        if (len(scFour[1]) < shortest and len(scFour[1]) != 0):
            shortest = len(scFour[1])
            final_output = scFour
            final_sc = 4
    except:
        pass
        
    print("Final Scenario: ",final_sc)
    print(final_output)
    
    if (final_sc == 0):
        return -1
    
    return final_output
        

def calculateRoutes(start_coord,end_coord,mode):
    if(mode == "walk"):
        # Call aStar function --> return walk_route
        result = routeAstar(start_coord,end_coord,G)
        walk_route = convertRoute(result)

        return walk_route

    elif(mode == "mrt"):
        # Call aStar function --> return mrt_route
        result = LRT(EastLoopG,WestLoopG,start_coord,end_coord)
        #print("result- ",result)
        #if(type(result) is None or result is not 0):
        try:
            if (result is not 0):         
                mrt_route = []
                for i in range(len(result)):
                    mrt_route.append(convertRoute(result[i]))
                # call heuristic see if bus or walk to endpoint
                # walk_start_coord = (mrt_route[-1][-1][0],mrt_route[-1][-1][1])
                # result_walk = routeAstar(walk_start_coord,end_coord,G)
                # walk_route = convertRoute(result_walk)
                # output = [("mrt",mrt_route),("walk",walk_route)]
                # return output
                
                endStationCoord = (mrt_route[-1][-1][0], mrt_route[-1][-1][1])
                dist = getDistanceKM(endStationCoord, end_coord)
                # print("\nDistance:")
                # print(dist)
                walk_start_coord = (mrt_route[-1][-1][0], mrt_route[-1][-1][1])
                result_walk = routeAstar(walk_start_coord, end_coord, G)
                walk_route = convertRoute(result_walk)
                output = [("mrt",mrt_route),("walk",walk_route)]
                # if (dist < 0.5):
                #     walk_start_coord = (mrt_route[-1][-1][0], mrt_route[-1][-1][1])
                #     result_walk = routeAstar(walk_start_coord, end_coord, G)
                #     walk_route = convertRoute(result_walk)
                #     output = [("mrt",mrt_route),("walk",walk_route)]
                # else:
                #     bus_start = ox.get_nearest_node(BusG, endStationCoord)
                #     bus_end = ox.get_nearest_node(BusG, end_coord)
                #     bus_route = getShortestBusRoute(bus_start,bus_end)
                #     print("bus-route")
                #     print(bus_route)
                    
                #     if(bus_route == -1 ):
                #         return -1
                    
                #     walk_start_coord = bus_route[2][-1]
                #     result_walk = routeAstar(walk_start_coord, end_coord, G)
                #     walk_route = convertRoute(result_walk)
                #     output = [("mrt",mrt_route),("bus",bus_route),("walk",walk_route)]
                #     print("\noutput\n")
                #     print(output)
                    # pass
                    #run Bus Algo here
                    #output = [("mrt",mrt_route),("bus",bus_route)]
                return output
            else:
                return -2
        except TypeError: #if result is None
            return -2

    elif (mode == "bus"): # Lat, Long (y,x)
        
        # Generate bus route
        bus_start = ox.get_nearest_node(BusG, start_coord)
        bus_end = ox.get_nearest_node(BusG, end_coord)
        bus_result = getShortestBusRoute(bus_start,bus_end)

        # break if no result
        if(bus_result == -1 ):
            return -1
        
        # Walk to bus stop
        # first_bus_coord = (BusG.nodes[bus_start]['x'],BusG.nodes[bus_start]['y'])
        # print("1 = ",first_bus_coord)
        # walk_to_bus =  routeAstar(start_coord,first_bus_coord,G);
        # walk_to_bus_result = convertRoute(walk_to_bus)
        # print("\nwalking to bus stop\n")
        # print(walk_to_bus_result)
        # print("\n")
        
        bus_route = bus_result[1]
        bus_last = bus_route[-1]
        
        # Walk from bus stop to destination
        result_walk = routeAstar(bus_last, end_coord, G)
        walk_route = convertRoute(result_walk)
        result = [bus_result,("walk",walk_route),("Start",start_coord)]
        return result
  
    else:
        return -1


@app.route('/')
def index():
    punggol = (1.3984, 103.9072)
    error = None
    return render_template('index.html')


@app.route('/posted', methods=['POST'])
def posted():
    start = request.form['start']
    end = request.form['end']
    mode = request.form['mode']

    # Split form value and convert to tuple of float
    start_coord = (float(start.split(",")[0]),float(start.split(",")[1]))
    end_coord = (float(end.split(",")[0]),float(end.split(",")[1]))

    # Calculate Route
    output = calculateRoutes(start_coord,end_coord,mode)
    print(output)
    if (type(output) is int):
        if(mode == "mrt"):
            err = "The MRT/LRT station is too close. Recommend to walk instead."
        elif(mode == "bus"):
            err = "There are no bus routes."
        return jsonify({'error' : err})
    else:
        return jsonify({'mode':mode,'array':output})

    return jsonify({'error' : 'Missing data!'})

if __name__ == '__main__':
    app.run(debug=True)
