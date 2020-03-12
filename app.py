from flask import Flask, render_template, request, jsonify
from aStar import testRouteAstar
import osmnx as ox
import networkx as nx


app = Flask(__name__)
punggol = (1.4052585, 103.9023302)
G = ox.graph_from_point(punggol, distance=2500, truncate_by_edge=True, network_type="walk")# quick plot

# @app.route('/route_name', methods=['GET', 'POST'])
@app.route('/')
def index():
    punggol = (1.3984, 103.9072)
    error = None
    return render_template('index.html')


@app.route('/posted', methods=['POST'])
def posted():
    start = request.form['start']
    end = request.form['end']
    
    print('start = ', start)
    print('end =', end)

    # Split form value and convert to tuple of float
    start_coord = (float(start.split(",")[0]),float(start.split(",")[1]))
    end_coord = (float(end.split(",")[0]),float(end.split(",")[1]))

    # Call aStar function --> return array
    arr = testRouteAstar(start_coord,end_coord,G);
    
    if start and end:
        return jsonify({'start': start_coord,'end': end_coord,'array':arr})
        
    return jsonify({'error' : 'Missing data!'})

if __name__ == '__main__':
    app.run(debug=True)
