Home@Punggol
=======
![](demo.gif)
---

Installation Guide
------
**System Requirements:**  
- Python 3.6 and above  


**PIP install**  
``pip install overpy flask osmnx`` 

If there is an error, please use the following links (inorder) and download the ``.whl`` file and manually install.  
1. https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal  
2. https://www.lfd.uci.edu/~gohlke/pythonlibs/#rtree  
3. https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely  
4. https://www.lfd.uci.edu/~gohlke/pythonlibs/#fiona  
---
Running the application  
------

``python app.py``  
or  
``python3 app.py``  

---
Project outline
-----

This project is created by Singapore Intitsute of Technology's students from Team 3 (Lab group 04).  

The team was tasked to build an application to allow its users to be able to navigate around Punggol District by providing the start and end point with the different types of route optimiztion.

---
Outcome
-----

### Route optimiztion available:
- LRT - Take LRT<sup>1</sup>, then directed to take bus<sup>1</sup> and lastly walk towards end destination.
- Bus - Take bus<sup>1</sup> and walk towards end destination.
- Walk - Walk towards end destinaton.  
<sub>1 - Only if needed, the algorithm will decide</sub>

### Algorithms:
#### Walking Algorithm  
A* algorithm is implemented to do our pathfinding, where heuristics is calculated by
``f(n) = g(n) + h(n)``.
- ``g(n)`` is the distance taken to reach a certain node, 
- ``h(n)`` is the euclidean distance from the certain node to end point

Using ``f(n)`` as the priority therefore, ensuring that the
algorithm will always find the shortest path for the user and in the simplest computation complexity.
 
#### Bus Routing Algorithm
Greedy Algorithm is implmented, where it will always choose the route that has the least amount of bus service changes. This approach is preferred over the shortest path to reduce inconvenience in a real world scenario since the shortest path requires the user to make multiple bus service changes.

 this is better as compared to the shortest path. Because the shortest path require much changes in bus service, causing inconvenience for the users.

#### LRT Algorithm
Breadth-first Search Algorithm is implemented, it will search in both clockwise and anti-clockwise, until it is able to reach the end station.

### Algorithm Complexity (Big-O)
Bus Algorithm: **O(n<sup>2</sup>)**  
  
Walk Algorithm: **O(<sub>log</sub> |E + V|)**  
  
LRT: **O(n)**  

### Data Structures
- Multi-Digraph 
- Priority Queue with heapq
- Adjacency Matrix
- Array
- Tuple

### Libraries
- [OSMNx](https://osmnx.readthedocs.io/en/stable/) - Walking and LRT Network  
- [NetworkX](https://networkx.github.io/) - Main Digraph Framework  
- [Overpass](https://pypi.org/project/overpy/) API - Bus Network  
- [heapq](https://docs.python.org/2/library/heapq.html) - Priority Queue for A* Algorithm  
- [Flask](https://flask.palletsprojects.com/en/1.1.x/) - Micro web framework
- [LeafletJS](https://leafletjs.com/) - Interactive Maps
- [jQuery](https://jquery.com) - Javascript Library
- [jQuery UI](https://jqueryui.com/) - Javascript Library

### Contribution

- YEO YUE HENG (1902613) - LRT Algorithm & integration
- TAN FU WEI (1902130) - Walk Algorithm & integration
- LEONG ZHI KAI (1902620) - Bus Algorithm & integration
- WONG ZEN KIT (1902638) - GUI & integration
- YEO YAO WEI NELSON (1902657) - Research shelter path data
- WILLIE CHUA (1902647) - Poster and Video 




