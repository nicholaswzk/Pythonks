bounds = new L.LatLngBounds(
	new L.LatLng(1.37, 103.88),
	new L.LatLng(1.44, 103.93)
);
var mapOptions = {
	center: [1.3984, 103.9072],
	zoom: 13,
	maxBounds: bounds,
	maxBoundsViscosity: 1.0
};

// // Creating a map object
var map = new L.map("map", mapOptions);
var CartoDB_Positron = L.tileLayer(
	"https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
	{
		attribution:
			'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
		subdomains: "abcd",
		minZoom: 15
	}
);
map.addLayer(CartoDB_Positron);
var FG = L.featureGroup();

// coordinate - (lat,long)
// id - 0 : start
//      1 : end
//      2 : bus
//      3 : mrt
function plotMarker(coord, id, msg) {
	var sicon = L.icon({
		iconUrl: "../static/images/Gps.svg",
		iconSize: [20, 68]
	});
	var eicon = L.icon({
		iconUrl: "../static/images/Pin.svg",
		iconSize: [24, 70],
		iconAnchor: [12, 43]
	});
	var bicon = L.icon({
		iconUrl: "../static/images/Bus_marker.svg",
		iconSize: [24, 70],
		iconAnchor: [12, 50]
	});
	var micon = L.icon({
		iconUrl: "../static/images/LRT_Marker_Purple.svg",
		iconSize: [24, 70],
		iconAnchor: [12, 50]
	});
	var m = {};
	if (id == 0) {
		m = L.marker(coord, { title: "Start", icon: sicon });
	}
	if (id == 1) {
		m = L.marker(coord, { title: "End", icon: eicon });
	}
	if (id == 2) {
		if (msg != "") {
			m = L.marker(coord, { title: msg, icon: bicon });
		} else {
			m = L.marker(coord, { icon: bicon });
		}
	}
	if (id == 3) {
		if (msg != "") {
			m = L.marker(coord, { title: msg, icon: micon });
		} else {
			m = L.marker(coord, { icon: micon });
		}
	}
	if (msg != "") {
		m.bindPopup(msg);
	}
	m.addTo(FG);
}

// Roughly draw walking route
function quickConnect(latlngs) {
	L.polyline(latlngs, { color: "grey", weight: "3", dashArray: "5, 10", dashOffset: "0" }).addTo(FG);
}

function drawWalk(latlngs, flag) {
	// Get new start & end point from osmnx
	var start_point = latlngs[0];
	var end_point = latlngs[latlngs.length - 1];

	if (flag == 0) {
		plotMarker(start_point, 0, "");
		// L.marker(start_point, { icon: sicon }).addTo(FG);
	}
	plotMarker(end_point, 1, "");
	//L.marker(end_point, { icon: eicon }).addTo(FG);
	L.polyline(latlngs, {
		color: "grey",
		weight: "3",
		dashArray: "5, 10",
		dashOffset: "0"
	}).addTo(FG);
}

// Returns EndPoint Coordinates
function drawMRT(latlngs) {
	// Get new start & end point from osmnx
	if (latlngs.length > 1) {
		var first_route = latlngs[0];
		var start_first_route = latlngs[0][0];
		var end_first_route = latlngs[0][latlngs[0].length - 1];

		var sec_route = latlngs[1];
		var start_sec_route = latlngs[1][0];
		var end_sec_route = latlngs[1][latlngs[1].length - 1];
		var chg_route = [end_first_route, start_sec_route];

		// draw routes and markers
		plotMarker(start_first_route, 0, "");
		plotMarker(start_sec_route, 3, "Interchange");
		plotMarker(end_sec_route, 3, "Alight");
		L.polyline(latlngs[0], { color: "purple" }).addTo(FG);
		L.polyline(chg_route, { color: "grey", weight: "3", dashArray: "5, 10", dashOffset: "0" }).addTo(FG);
		L.polyline(latlngs[1], { color: "purple" }).addTo(FG);

		return end_sec_route;

	} else {
		var start_point = latlngs[0][0];
		var end_point = latlngs[0][latlngs[0].length - 1];

		// draw routes and markers
		plotMarker(start_point, 0, "");
		plotMarker(end_point, 3, "Alight");
		L.polyline(latlngs, { color: "purple" }).addTo(FG);

		return end_point;
	}
}

function drawBus(array) {
	var route = array[1];
	var stops = array[2];
	var buses = array[3];

	if (stops.length == 2) {
		var walk_to_start = [stops[0], route[0]];
		plotMarker(route[0], 2, "Take " + buses);
		plotMarker(route[route.length - 1], 2, "Alight");
		L.polyline(route, { color: "#46485A" }).addTo(FG);
	} else {
		plotMarker(route[0], 2, "Take " + buses[0]);
		plotMarker(stops[1], 2, "Change to " + buses[1]);
		plotMarker(route[route.length - 1], 2, "Alight here");
		L.polyline(route, { color: "#46485A" }).addTo(FG);
	}
}

function drawRoute(mode, latlngs) {
	// Clear current layers
	map.removeLayer(FG);
	FG = L.featureGroup();

	// remove loading animation
	removeLoad();

	// if else mode
	if (mode == "walk") {
		drawWalk(latlngs, 0);
	}

	// latlngs = [[mrt_flag][mrt_array],[walk_flag][walk_array]]
	else if (mode == "mrt") {
		var x = drawMRT(latlngs[0][1]);
		if (latlngs[1][0] == "walk" && latlngs[1][1].length != 0) {
			quickConnect([x, latlngs[1][1][0]]);
			drawWalk(latlngs[1][1], 1);
		} else {
			var end_point = latlngs[0][1][0][latlngs[0][1][0].length - 1];
			L.marker(end_point, { icon: eicon }).addTo(FG);
		}
	}
	// bus_result = [["BUS"][bus_array][bus_stops_array][bus_num]]
	// latlngs = [bus_result,("walk",walk_route),("Start",1st bustop coord)]
	else if (mode == "bus") {
		var st_connect = [latlngs[2][1], latlngs[0][1][0]];
		var ed_connect = [latlngs[0][1][latlngs[0][1].length - 1], latlngs[1][1][0]];
		plotMarker(latlngs[2][1], 0, "");
		quickConnect(st_connect);
		drawBus(latlngs[0], 0);
		quickConnect(ed_connect);
		drawWalk(latlngs[1][1], 1);
	}

	FG.addTo(map);
	map.fitBounds(FG.getBounds());
}
