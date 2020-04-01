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
// Mapbox
// L.mapbox.accessToken = 'pk.eyJ1IjoiemVudGFybyIsImEiOiJjazZic2ZvOWswa28xM2ttZ25saXJsb2syIn0.PTJ6ZEWwsaUTCh_pxRkLGg';
// var map = L.mapbox.map('map','mapbox.streets',mapOptions)
//     .setView([40, -74.50], 9)
//     .addLayer(L.mapbox.styleLayer('mapbox://styles/mapbox/streets-v11'));

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
var start_marker = {};
var end_marker = {};
var FG = L.featureGroup();
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

// plotMarker(coordinate,marker id,msg)
// coordinate - (lat,long)
// id - 0 : start
//      1 : end
//      2 : bus
//      3 : mrt
function plotMarker(coord,id,msg){
	var m = {};
	if (id == 0){
		m = L.marker(coord, { icon: sicon });
	}
	if (id == 1){
		m = L.marker(coord, { icon: eicon });
	}
	if (id == 2){
		m= L.marker(coord, { icon: bicon });
	}
	if (id == 3){
		m = L.marker(coord, { icon: micon });
	}
	if (msg != ""){
		m.bindPopup(msg);
	}
	m.addTo(FG);
}

// Roughly draw walking route
function quickConnect(latlngs){
	var start_point = latlngs[0];
	var end_point = latlngs[latlngs.length - 1];	
	L.polyline(latlngs, {color: 'grey', weight: '3',  dashArray: '5, 10', dashOffset: '0'}).addTo(FG);
}

function drawWalk(latlngs, flag) {
	// Get new start & end point from osmnx
	var start_point = latlngs[0];
	var end_point = latlngs[latlngs.length - 1];

	if (flag == 0) {
		start_marker = L.marker(start_point, { icon: sicon }).addTo(FG);
	}
	end_marker = L.marker(end_point, { icon: eicon }).addTo(FG);
	//L.polyline(latlngs, { color: "grey" }).addTo(FG);
	L.polyline(latlngs, {color: 'grey', weight: '3',  dashArray: '5, 10', dashOffset: '0'}).addTo(FG);
}

// Returns EndPoint Coordinates
function drawMRT(latlngs, len) {
	// Get new start & end point from osmnx
	if (len > 1) {
		var first_route = latlngs[0];
		var start_first_route = latlngs[0][0];
		var end_first_route = latlngs[0][latlngs[0].length - 1];

		var sec_route = latlngs[1];
		var start_sec_route = latlngs[1][0];
		var end_sec_route = latlngs[1][latlngs[1].length - 1];
		var chg_route = [end_first_route, start_sec_route];

		// draw markers
		plotMarker(start_first_route,0,"");

		// draw routes
		L.polyline(latlngs[0], { color: "purple" }).addTo(FG);
		L.polyline(chg_route, {color: 'grey', weight: '3',  dashArray: '5, 10', dashOffset: '0'}).addTo(FG);
		L.polyline(latlngs[1], { color: "purple" }).addTo(FG);

		plotMarker(start_sec_route,3,"Interchange");
		plotMarker(end_sec_route,3,"Alight");
		return end_sec_route;

	} else {
		var start_point = latlngs[0][0];
		var end_point = latlngs[0][latlngs[0].length - 1];
		console.log("start: "+start_point);
		console.log("end: "+end_point);
		// draw routes
		plotMarker(start_point,0,"");
		plotMarker(end_point,3,"Alight");
		L.polyline(latlngs, { color: "purple" }).addTo(FG);
		return end_point;
	}
}

function drawBus(array) {
	var flag = array[0];
	var route = array[1];
	var stops = array[2];
	var buses = array[3];

	if (stops.length == 2) {
		var walk_to_start = [stops[0], route[0]];
		L.marker(route[0], { title: buses, icon: bicon })
			.addTo(FG)
			.bindPopup("Take " + buses);
		//testing only
		L.marker(route[route.length - 1], {icon: bicon})
			.addTo(FG)
			.bindPopup("Alight");
		//L.polyline(walk_to_start, { color: "grey" }).addTo(FG);
		L.polyline(route, { color: "#46485A" }).addTo(FG);
	} else {
		var walk_to_start = [stops[0], route[0]];
		L.marker(route[0], { title: buses[0], icon: bicon })
			.addTo(FG)
			.bindPopup("Take " + buses[0]);
		L.marker(stops[1], { title: buses[1], icon: bicon })
			.addTo(FG)
			.bindPopup("Change to " + buses[1]);
		// testing only
		L.marker(route[route.length - 1], {icon: bicon})
			.addTo(FG)
			.bindPopup("Alight");
		//L.polyline(walk_to_start, { color: "grey" }).addTo(FG);
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
	} else if (mode == "mrt") {
		var x = drawMRT(latlngs[0][1], latlngs[0][1].length);
		if (latlngs[1][0] == "walk" && latlngs[1][1].length != 0 ) {
			quickConnect([x,latlngs[1][1][0]]);
			drawWalk(latlngs[1][1], 1);
		}
		else{
			var end_point = latlngs[0][1][0][latlngs[0][1][0].length - 1];
			end_marker = L.marker(end_point, { icon: eicon }).addTo(FG);
		}
	} else if (mode == "bus") {
		if (latlngs[0][0] != "BUS") {
			console.log("Error")
		} else {
			var st = [latlngs[2][1],latlngs[0][1][0]];
			plotMarker(latlngs[2][1],0,"");
			quickConnect(st);
			drawBus(latlngs[0],0);
			drawWalk(latlngs[1][1],1);
		}
	}

	FG.addTo(map);
	map.fitBounds(FG.getBounds());
}
