// Globals
var sObj = {};
var eObj = {};
var addr = [];
var mrts = [
	{ label: "Coral Edge LRT", lat: 1.3939318, lon: 103.9125723 },
	{ label: "Cove LRT", lat: 1.3994643, lon: 103.9058522 },
	{ label: "Damai LRT", lat: 1.4052523, lon: 103.9085982 },
	{ label: "Kadaloor LRT", lat: 1.399601, lon: 103.9164448 },
	{ label: "Meridian LRT", lat: 1.39635375, lon: 103.9075887 }, // recheck coords 
	{ label: "Nibong LRT", lat: 1.4118314, lon: 103.9003049 },
	{ label: "Oasis LRT", lat: 1.4023166, lon: 103.9126843 },
	{ label: "Punggol MRT", lat: 1.4052551, lon: 103.9023538 },
	{ label: "Punggol Point LRT", lat: 1.4168814, lon: 103.9066298 },
	{ label: "Riviera LRT", lat: 1.3945492, lon: 103.9161044 },
	{ label: "Sam Kee LRT", lat: 1.4097219, lon: 103.9048903 },
	{ label: "Samudera LRT", lat: 1.4159537, lon: 103.9021398 },
	{ label: "Soo Teck LRT", lat: 1.4053014, lon: 103.8972748 },
	{ label: "Sumang LRT", lat: 1.4085322, lon: 103.8985342 },
	{ label: "Teck Lee LRT", lat: 1.4127373, lon: 103.9065808 }
];
var awidth = $("#start").innerWidth();
var $end = $("#end");
var $start = $("#start");
var labels = ["mrt", "bus", "shelter", "walk"];

// typing timer
$.fn.donetyping = function(callback) {
	var _this = $(this);
	var x_timer;
	_this.keyup(function() {
		clearTimeout(x_timer);
		x_timer = setTimeout(clear_timer, 300);
	});

	function clear_timer() {
		clearTimeout(x_timer);
		callback.call(_this);
	}
};

function doAutocomplete($input) {
	// If user searching endpoint, call API
	if ($input.is("#end")) {
		geocode($input);
	}
	awidth = $input.innerWidth();
	$(".ui-menu").css("max-width", awidth);

	if ($input.is("#start")) {
		$input.autocomplete({
			delay: 0,
			source: mrts,
			select: function(event, ui) {
				if ($input.is("#start")) {
					sObj = ui.item;
				}
			}
		});
	} else if ($input.is("#end")) {
		$input.autocomplete({
			delay: 0,
			source: function(request, resolve) {
				// fetch new values with request.term
				resolve(addr.slice(0, 7));
			},
			select: function(event, ui) {
				if ($input.is("#end")) {
					eObj = ui.item;
				}
			}
		});
	}
}

// function to show loading animation
function showLoad() {
	$(".submit").addClass("run");
	$(".loader").addClass("run");
}

// Call LocationIQ API
function geocode($input) {
	addr.length = 0;
	var str = $input.val();
	var settings = {
		async: true,
		crossDomain: true,
		url: "https://api.locationiq.com/v1/autocomplete.php",
		data: {
			key: "dc7e78d5094041",
			q: str,
			limit: 6,
			countrycodes: "SG"
		},
		method: "GET"
	};
	$.ajax(settings).done(function(response) {
		for (var i = 0; i < response.length; i++) {
			if (response[i].display_name.indexOf("Punggol") > -1) {
				// Filter to Punggol only
				var obj = {
					label: response[i].display_name,
					lat: response[i].lat,
					lon: response[i].lon
				};
				addr.push(obj);
			}
		}
	});
}
$(document).ready(function() {
	// Radiobutton behaviour
	$("input[name='mode']").change(function(e) {
		var rid = $(this).attr("id");
		if (rid.length > -1) {
			cur = rid.substring(0, rid.length - 3);
			for (var l = 0; l < labels.length; l++) {
				if (labels[l] != cur) {
					$("#" + labels[l]).removeClass("active");
				} else {
					$cur = $("#" + cur);
					if ($cur.hasClass("active")) {
						$cur.removeClass("active");
					} else {
						$cur.addClass("active");
					}
				}
			}
		}
	});

	$start.donetyping(function(callback) {
		doAutocomplete($start);
	});

	$end.donetyping(function(callback) {
		doAutocomplete($end);
	});

	// Send form data to backend via ajax
	$("form").on("submit", function(event) {
		console.log(sObj.lat + "," + sObj.lon);
		console.log(eObj.lat + "," + eObj.lon);
		if (
			$("#start").val() != "" &&
			$("#end").val() != "" &&
			$.isEmptyObject(sObj) &&
			$.isEmptyObject(eObj)
		) {
			console.log("Missing input");
		} else {
			showLoad();
			$.ajax({
				data: {
					start: sObj.lat + "," + sObj.lon,
					end: eObj.lat + "," + eObj.lon
					//$('input[name="mode"]:checked').val(); // Send flag
				},
				type: "POST",
				url: "/posted"
			}).done(function(data) {
				// do after sending data
				if (data.error) {
					console.log(data.error);
				} else {
					//testDrawMarker(data.start,data.end);
					console.log("From flask: Start = " + data.start);
					console.log("From flask: End = " + data.end);
					drawRoute(data.array);
				}
			});
		}
		// prevent html postback and use jqeury/ ajax instead
		event.preventDefault();
	});
});
