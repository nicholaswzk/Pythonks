from flask import Flask, render_template
import folium
import osmnx as ox
import networkx as nx

app = Flask(__name__)

@app.route('/')
def index():
    punggol = (1.3984, 103.9072)
    G = ox.graph_from_point(punggol, distance=2000)
    mrt = ox.geocode('Punggol, Punggol Central, Punggol, Northeast, 828868, Singapore')
    hdb = ox.geocode('Waterway Sunray, 659B, Punggol East, Punggol, Northeast, 822659, Singapore')

    # Get nearest node from geocode
    mrt_node = ox.get_nearest_node(G,mrt,method='euclidean',return_dist=False)
    hdb_node = ox.get_nearest_node(G,hdb,method='euclidean',return_dist=False)

    # Set shortest_path route
    route = nx.shortest_path(G, mrt_node, hdb_node)

    # Generate Folium Map at Punggol area
    folium_map = folium.Map(width='80%',height='100%',location=punggol,tiles='cartodbpositron',zoom_start=14)
    
    # Set route on existing folium map
    m = ox.plot.plot_route_folium(G, route, route_map=folium_map,route_color='green')
    # Add Markers to folium map
    folium.Marker(location=mrt,icon=folium.Icon(color='red')).add_to(folium_map)
    folium.Marker(location=hdb,icon=folium.Icon(color='blue')).add_to(folium_map)
    folium_map.save('templates/map.html')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)