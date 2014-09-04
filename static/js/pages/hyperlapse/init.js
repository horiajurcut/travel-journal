var GHyperlapse = {
	origin: null,
	destination: null,
	waypoints: [],
	places: [],
	loadingMessages: [
		'Caffeinating our Development team!',
		'Locating the required gigapixels to render...',
		'Shovelling coal into the server...',
		'Please wait... the architects are still drafting!',
		'Warming up Large Hadron Collider...',
		'Yes there really are magic elves with an abacus working frantically in here.',
		'Elf down! We are cloning the elf that was supposed to get you the data. Please wait.',
		'1,000,000 bottles of beer on the wall...',
		'Have you lost weight?',
		'Are we there yet?',
		'Who is General Failure and why is he reading my hard disk?',
		'Transporting you into the future one second at a time...',
		'Spinning the wheel of fortune...'
	],
	init: function () {
		GHyperlapse._processWaypoints();

		var hyperlapse = new Hyperlapse(document.getElementById('pano'), {
			zoom: 2,
			elevation: 50,
			distance_between_points: 1,
			max_points: 150,
			width: 800,
			height: 400,
			millis: 700
		});

		hyperlapse.onError = function(e) {
			console.log(e);
		};

		hyperlapse.onFrame = function() {

		};

		hyperlapse.onRouteProgress = function(e) {
			// Stuff happens while computing the Route
			if (hyperlapse.length() % 20 == 9) {
				$('.hyperlapse__progress-wrap h1').html(GHyperlapse.loadingMessages[Math.round(Math.random() * (GHyperlapse.loadingMessages.length - 1))]);
			}
		}		

		hyperlapse.onRouteComplete = function(e) {
			hyperlapse.load();
		};

		hyperlapse.onLoadProgress = function(e) {
			var p = 100 - parseInt(Math.floor((e.position + 1) / hyperlapse.length() * 100), 10),
				m = p % GHyperlapse.loadingMessages.length;

			if (p < 0) {
				p = 0;
			}

			$('.hyperlapse__progress-wrap progress').val(p);
			
			if (p % 20 == 9) {
				$('.hyperlapse__progress-wrap h1').html(GHyperlapse.loadingMessages[Math.round(Math.random() * (GHyperlapse.loadingMessages.length - 1))]);
			}
		}

		hyperlapse.onLoadComplete = function(e) {
			GHyperlapse._removeLoader();
			hyperlapse.play();
		};

		// Google Maps API stuff here...
		var directions_service = new google.maps.DirectionsService();

		var route = {
			request:{
				origin: GHyperlapse.origin,
				destination: GHyperlapse.destination,
				waypoints: GHyperlapse.waypoints,
				optimizeWaypoints: true,
				travelMode: google.maps.DirectionsTravelMode.WALKING
			}
		};

		directions_service.route(route.request, function(response, status) {
			if (status == google.maps.DirectionsStatus.OK) {
				hyperlapse.generate({ route: response });
			} else {
				console.log(status);
			}
		});
	},
	_processWaypoints: function () {
		var o = GHyperlapse.places.shift(),
			d = GHyperlapse.places.pop();

		GHyperlapse.origin = new google.maps.LatLng(o.latitude, o.longitude);
		GHyperlapse.destination = new google.maps.LatLng(d.latitude, d.longitude);

		for (var i = 0; i < GHyperlapse.places.length; i++) {
			GHyperlapse.waypoints.push({
				location: new google.maps.LatLng(
					GHyperlapse.places[i].latitude,
					GHyperlapse.places[i].longitude
				)
			});
		}
	},
	_removeLoader: function () {
		$('.hyperlapse__progress-wrap').addClass('invisible');
		$('#pano').removeClass('invisible');
	}
};

$(document).ready(function () {
	var requests = [];

	// Get Waypoints
	var routeWaypoints = $.ajax({
		type: 'GET',
		url:  '/tj/search/places/' + $('#hyperlapse').attr('data-plan-id'),
		beforeSend: function() {

		},
		success: function(result) {
			GHyperlapse.places = result;
		},
		error: function() {

		}
	});
	requests.push(routeWaypoints);

	// Initialize Map after all the requests have been handled
	var callback = function(results) {
		GHyperlapse.init();
	}

	$.when.all(requests).done(callback);
});