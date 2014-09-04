StreetViewPage = {
	map:         null,
	svOrigin:    null,
	origin:      null,
	destination: null,
	places:      [],
	place_bkp:   [],
	waypoints:   [],
	mappings: {
		'turn-left':         'fa fa-arrow-left',
		'turn-right':        'fa fa-arrow-right',
		'turn-slight-right': 'fa fa-chevron-right',
		'turn-slight-left':  'fa fa-chevron-left',
		'straight':          'fa fa-arrow-up'
	},
	types: {
		'cafe':          'fa fa-coffee',
		'bar':           'fa fa-glass',
		'restaurant':    'fa fa-cutlery',
		'food':          'fa fa-cutlery',
		'bakery':        'fa fa-cutlery',
		'park':          'fa fa-leaf',
		'store':         'fa fa-gift',
		'shoe-store':    'fa fa-gift',
		'movie_theater': 'fa fa-film'
	},
	initMap: function () {
		/* Enable Street View */
		var panoramaOptions = {
			position: StreetViewPage.svOrigin,
			pov: {
				heading: 0,
				pitch: 0
			},
			zoom: 0,
			zoomControlOptions: {
				position: google.maps.ControlPosition.LEFT_CENTER,
				style: google.maps.ZoomControlStyle.SMALL
			},
			panControlOptions: {
				position: google.maps.ControlPosition.LEFT_CENTER
			},
			addressControl: false,
			addressControlOptions: {
				position: google.maps.ControlPosition.BOTTOM_CENTER
			},
			linksControl: true,
			clickToGo: true
		};

		if (isMobile.phone || isMobile.tablet) {
			panoramaOptions.zoom = 1;
		}

		StreetViewPage.map = new google.maps.StreetViewPanorama(document.getElementById('map'), panoramaOptions);
		StreetViewPage.map.setVisible(true);

		/* Get Directions */
		var directionsService = new google.maps.DirectionsService();

		/* Define Route */
		route = {
			origin:                   StreetViewPage.origin,
			destination:              StreetViewPage.destination,
			waypoints:                StreetViewPage.waypoints,
			optimizeWaypoints:        true,
			provideRouteAlternatives: false,
			travelMode:               google.maps.DirectionsTravelMode.WALKING
		};

		directionsService.route(route, function(result, status) {
			if (status == google.maps.DirectionsStatus.OK) {
				StreetViewPage._buildDirections(result.routes[0]);
			}
		});
	},
	_prepareWaypoints: function () {
		var o = StreetViewPage.places_bkp.shift(),
			d = StreetViewPage.places_bkp.pop();

		StreetViewPage.origin = new google.maps.LatLng(o.latitude, o.longitude);
		StreetViewPage.destination = new google.maps.LatLng(d.latitude, d.longitude);

		for (var i = 0; i < StreetViewPage.places_bkp.length; i++) {
			StreetViewPage.waypoints.push({
				location: new google.maps.LatLng(
					StreetViewPage.places_bkp[i].latitude,
					StreetViewPage.places_bkp[i].longitude
				)
			});
		}
	},
	_buildDirections: function(directions) {
		var i, j;
		var $container = $('#directions'),
			$currentLeg = null,
			$currentStep = null,
			$steps = null,
			legs = directions.legs;

		for (i = 0; i < legs.length; i++) {
			$currentLeg = $(document.createElement('div'));
			$currentLeg.addClass('leg');
			
			var type = 'fa fa-map-marker',
				typeArr = [];
			if (StreetViewPage.places[i].types) {
				typeArr = StreetViewPage.places[i].types.split('|');
				if (typeArr[0] && StreetViewPage.types[typeArr[0]] !== undefined) {
					type = StreetViewPage.types[typeArr[0]]; 
				}
			}

			$currentLeg.append($(document.createElement('h3')).addClass('leg-title')
				.attr('data-lat', StreetViewPage.places[i].latitude)
				.attr('data-lng', StreetViewPage.places[i].longitude)
				.attr('title', StreetViewPage.places[i].name + ' located at ' + StreetViewPage.places[i].vicinity)
				.html((i + 1) + '. ' + StreetViewPage.places[i].name)
				.prepend($(document.createElement('i')).addClass(type)));

			

			$steps = $(document.createElement('div'));
			$steps.addClass('leg-steps');

			$steps.append($(document.createElement('ul')));

			for (j = 0; j < legs[i].steps.length; j++) {
				$currentStep = $(document.createElement('li'));

				// Find current locations
				var lat = 0, lng = 0, points = [];

				points = legs[i].steps[j].lat_lngs;
				// lat = points[Math.ceil(points.length / 2)].lat();
				// lng = points[Math.ceil(points.length / 2)].lng();

				lat = points[0].lat();
				lng = points[0].lng();

				$currentStep.attr('data-lat', lat);
				$currentStep.attr('data-lng', lng);

				$currentStep.append($(document.createElement('div')).addClass('step-distance')
					.html(legs[i].steps[j].distance.value + ' m'));

				// Directions Icons
				var icon = null;

				if (legs[i].steps[j].maneuver !== '' && StreetViewPage.mappings[legs[i].steps[j].maneuver] !== undefined) {
					$currentStep.append($(document.createElement('i')).addClass(StreetViewPage.mappings[legs[i].steps[j].maneuver]));
				} else {
					$currentStep.append($(document.createElement('i')).addClass('fa fa-dot-circle-o'));
				}

				$currentStep.append((j+1) + '. ' + legs[i].steps[j].instructions);


				$steps.find('ul').append($currentStep);
			}

			$currentLeg.append($steps);

			$currentLeg.append($(document.createElement('div')).addClass('leg-info')
				.attr('title', legs[i].distance.text + ', about ' + legs[i].duration.text)
				.append($(document.createElement('i')).addClass('fa fa-info-circle'))
				.append(legs[i].distance.text + ', about ' + legs[i].duration.text));

			$container.append($currentLeg);
		}

		// Final Waypoint
		$currentLeg = $(document.createElement('div'));
		$currentLeg.addClass('leg');
		
		var type = 'fa fa-map-marker',
			typeArr = [];
		if (StreetViewPage.places[StreetViewPage.places.length - 1].types) {
			typeArr = StreetViewPage.places[i].types.split('|');
			if (typeArr[0] && StreetViewPage.types[typeArr[0]] !== undefined) {
				type = StreetViewPage.types[typeArr[0]]; 
			}
		}

		$currentLeg.append($(document.createElement('h3')).addClass('leg-title')
			.attr('data-lat', StreetViewPage.places[StreetViewPage.places.length - 1].latitude)
			.attr('data-lng', StreetViewPage.places[StreetViewPage.places.length - 1].longitude)
			.attr('title', StreetViewPage.places[i].name + ' located at ' + StreetViewPage.places[StreetViewPage.places.length - 1].vicinity)
			.html((StreetViewPage.places.length) + '. ' + StreetViewPage.places[StreetViewPage.places.length - 1].name)
			.prepend($(document.createElement('i')).addClass(type)));

		$container.append($currentLeg);
	},
	_getSVOrigin: function() {
		var sv = new google.maps.StreetViewService();

		/* Prepare locations */
		StreetViewPage._prepareWaypoints();
			
		sv.getPanoramaByLocation(StreetViewPage.origin, 50, function (data, status) {
			if (status == google.maps.StreetViewStatus.OK) {
				StreetViewPage.svOrigin = StreetViewPage.origin;
			} else {
				StreetViewPage.svOrigin = new google.maps.LatLng('37.42291810', '-122.08542120');
			}

			/* Init Map */
			StreetViewPage.initMap();
		});
	}
}

$(document).ready(function() {
	/* Get Map Information */
	var requests = [];

	var routeWaypoints = $.ajax({
		type: 'GET',
		url:  '/tj/search/places/' + $('#directions').attr('data-plan-id'),
		beforeSend: function() {

		},
		success: function(result) {
			StreetViewPage.places     = result;
			StreetViewPage.places_bkp = StreetViewPage.places.slice(); 
		},
		error: function() {

		}
	});
	requests.push(routeWaypoints);

	/* Initialize Map */
	var callback = function(results) {
		StreetViewPage._getSVOrigin();
	}

	$.when.all(requests).done(callback);

	/* Street View Events */
	$('#directions').on('click', '.leg .leg-steps ul li, .leg-title', function () {
		$('.leg-title, .leg .leg-steps ul li').removeClass('selected-step');
		$('.leg-title, .leg .leg-steps ul li').removeClass('previous-step');
		
		$(this).addClass('selected-step');
		$(this).prev().addClass('previous-step');

		var sv = new google.maps.StreetViewService(),
		    pos = new google.maps.LatLng(
				$(this).attr('data-lat'),
				$(this).attr('data-lng')
			);

		sv.getPanoramaByLocation(pos, 50, function (data, status) {
			if (status == google.maps.StreetViewStatus.OK) {
				StreetViewPage.map.setPosition(data.location.latLng);
			}
		})
	});
});