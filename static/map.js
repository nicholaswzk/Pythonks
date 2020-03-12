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
// Creating a map object
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
var path = {};

function drawRoute(latlngs) {
	// Clear current layers
	map.removeLayer(start_marker);
	map.removeLayer(end_marker);
	map.removeLayer(path);

	// Get new start & end point from osmnx
	var start_point = latlngs[0];
	var end_point = latlngs[latlngs.length - 1];

	var sicon = L.icon({
		iconUrl: "../static/images/Gps.svg",
		iconSize: [20, 68]
	});

	var eicon = L.icon({
		iconUrl: "../static/images/Pin.svg",
		iconSize: [24, 70]
	});

	// remove loading animation
	$(".submit").removeClass("run");
	$(".loader").removeClass("run");

	start_marker = L.marker(start_point, { icon: sicon }).addTo(map);
	end_marker = L.marker(end_point, { icon: eicon }).addTo(map);

	path = L.polyline(latlngs, { color: "purple" }).addTo(map);
	map.fitBounds(path.getBounds());
}
