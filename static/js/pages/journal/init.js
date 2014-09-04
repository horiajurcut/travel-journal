var Journal = {
	map:         null,
	origin:      {},
	destination: {},
	places:      [],
	places_bkp:  [],
	waypoints:   [],
	markers:     [],
	lastPopup:   null,
	isCentered:  false,
	initMap: function () {
		Journal._prepareMarkers();
		Journal._prepareWaypoints();
		Journal._drawMap();
	},
	_drawMap: function() {
		/* Configure Map */
		var mapOptions = {
			zoom: 16,
			zoomControl: true,
			scrollwheel: false,
			center: Journal.origin
		};

		/* Our Map Object */
		Journal.map = new google.maps.Map(document.getElementById('map'), mapOptions);

		/* Add Events to Map */
		google.maps.event.addListener(Journal.map, 'bounds_changed', function () {
			if (!Journal.isCentered) {
				Journal.map.setCenter(Journal.origin);
				Journal.isCentered = true;
			}
		});

		/* Add Markers to Map */
		for (var i = 0; i < Journal.markers.length; i++) {
			Journal.markers[i].setMap(Journal.map);
		}

		/* Get Directions */
		var displayOptions = {
			suppressMarkers:     true,
			suppressInfoWindows: true,
			preserveViewport:    true,
			polylineOptions: {
				options: {
					strokeColor: '#6599FF',
					strokeWeight: 5
				}
			},
		}
		var directionsService = new google.maps.DirectionsService();
		var directionsDisplay = new google.maps.DirectionsRenderer(displayOptions);

		/* Attach Directions to Map */
		directionsDisplay.setMap(Journal.map);

		/* Define Route */
		route = {
			origin:                   Journal.origin,
			destination:              Journal.destination,
			waypoints:                Journal.waypoints,
			optimizeWaypoints:        true,
			provideRouteAlternatives: true,
			travelMode:               google.maps.DirectionsTravelMode.WALKING
		};

		directionsService.route(route, function(result, status) {
			if (status == google.maps.DirectionsStatus.OK) {
				directionsDisplay.setDirections(result);
			}
		});
	},
	_prepareMarkers: function () {
		for (var i = 0; i < Journal.places.length; i++) {
			var popup = document.createElement('div');

			popup.className  = 'map-info-window';
			popup.innerHTML  = '<span class="title">' + Journal.places[i].name + '</span>';
			popup.innerHTML += '<span>' + Journal.places[i].vicinity + '</span>';
			popup.innerHTML += '<span>Rating: ' + Journal.places[i].rating + '</span>';

			var marker = new google.maps.Marker({
				icon: {
					url:        Journal.places[i].icon,
					size: new google.maps.Size(30, 30),
					scaledSize: new google.maps.Size(30, 30)
				},
				title: Journal.places[i].name,
				flat: true,
				position: new google.maps.LatLng(
					Journal.places[i].latitude,
					Journal.places[i].longitude
				),
				info: new google.maps.InfoWindow({
					content: popup
				})
			});

			/* Add Event to Marker */
			google.maps.event.addListener(marker, 'click', function () {
				if (Journal.lastPopup !== this.info) {
					if (Journal.lastPopup) {
						Journal.lastPopup.close();
					}
					this.info.open(Journal.map, this);
					Journal.lastPopup = this.info;
				}
			});

			Journal.markers.push(marker);
		}
	},
	_prepareWaypoints: function () {
		var o = Journal.places.shift(),
			d = Journal.places.pop();

		Journal.origin = new google.maps.LatLng(o.latitude, o.longitude);
		Journal.destination = new google.maps.LatLng(d.latitude, d.longitude);

		for (var i = 0; i < Journal.places.length; i++) {
			Journal.waypoints.push({
				location: new google.maps.LatLng(
					Journal.places[i].latitude,
					Journal.places[i].longitude
				)
			});
		}
	},
	buildVideo: function (videoId) {
		var $player = $(document.createElement('iframe'));

		$player.attr('class', 'youtube');
		
		$player.attr('type', 'text/html');
		$player.attr('src', 'http://www.youtube.com/embed/' + videoId + '?html5=1');
		
		$player.attr('frameborder', '0');
		
		$player.attr('width', '560');
		$player.attr('height', '315');

		return $player;
	},
	cleanUpVideos: function () {
		$('iframe.youtube').remove();
	},
	replaceProfileImages: function () {
		$('.review-avatar').each(function (index) {
			var $this = $(this);

			/* Load Photo only if user has one */
			if (parseInt($this.attr('data-has-photo'), 10) === 1) {
				var $profilePhoto = $(document.createElement('img'));

				$profilePhoto.addClass('review-avatar');

				$profilePhoto
					.load(function () {
						$this.replaceWith($profilePhoto);
					})
					.error(function () {
						console.log('Image not found on Google+ Servers');
					})
					.attr('src', 'https://plus.google.com/s2/photos/profile/' + $this.attr('data-author-id') + '?sz=300');
			}
		});	
	},
	replaceBackgroundImages: function () {
		$('.cover').each(function (index) {
			var $this = $(this);
			
			if (!isMobile.phone) {
				var	$background = $(document.createElement('img'));

				$background
					.load(function () {
						$this.attr('style', 'background-image: url(' + $this.attr('data-background-image') + ');');
						$(this).remove();
					})
					.error(function () {
						console.log('Image not found on Flickr Servers');
					})
					.attr('src', $this.attr('data-background-image'));
			} else {
				$this.attr('style', 'background-color: #57A3D1;');
			}
		});	
	},
	replaceHotelImages: function () {
		$('.hotel-photo-wrapper').each(function (index, value) {
			var $this = $(value),
			    $photo = $(document.createElement('img'));

			$photo
				.load(function () {
					$this.attr('style', 'background-image: url(' + $this.attr('data-hotel-img') + ');');
					$(this).remove();
				})
				.error(function () {
					console.log('Image not found on Expedia Servers');
				})
				.attr('src', $this.attr('data-hotel-img'));
		});
	},
	replacePlacesImages: function () {
		$('.place-photo-wrapper').each(function (index, value) {
			var $this = $(value),
			    $photo = $(document.createElement('img'));

			$photo
				.load(function () {
					$this.attr('style', 'background-image: url(' + $this.attr('data-place-img') + ');');
					$(this).remove();
				})
				.error(function () {
					console.log('Image not found on Google Servers');
				})
				.attr('src', $this.attr('data-place-img'));
		});
	},
	plotWeatherCharts: function () {
		/* Plot Weather Charts */
		Journal._drawWindSpeed();
		Journal._drawTempChart();
	},
	_drawWindSpeed: function () {
		var maxWindSpeed = parseFloat($('.weather__computed-stats').attr('data-wind-speed')),
		    over = false,
		    label = '';

		if (maxWindSpeed > 300) {
			over = true;
			maxWindSpeed = 300;
		}

		AmCharts.ready(function () {
			// create angular gauge
			var gaugeChart = new AmCharts.AmAngularGauge(),
				axisMiles,
				arrow;

			// miles axis
			var axisMiles = new AmCharts.GaugeAxis();
			axisMiles.startValue = 0;
			axisMiles.endValue = 300;
			axisMiles.radius = "80%";
			axisMiles.axisColor = "#80a8d9";
			axisMiles.tickColor = "#80a8d9";
			axisMiles.axisThickness = 3;

			var band_max = new AmCharts.GaugeBand();
			band_max.startValue = 250;
			band_max.endValue = 300;
			band_max.color = "#b72c34";

			var band_avg = new AmCharts.GaugeBand();
			band_avg.startValue = 200;
			band_avg.endValue = 250;
			band_avg.color = "#FEC14B";

			axisMiles.bands = [band_avg, band_max];

			gaugeChart.addAxis(axisMiles);

			// arrow
			arrow = new AmCharts.GaugeArrow();
			arrow.radius = "85%";
			arrow.color = "#80a8d9";
			arrow.innerRadius = 50;
			arrow.nailRadius = 50;
			arrow.nailAlpha = 0;
			arrow.nailBorderAlpha = 1;
			arrow.nailBorderThickness = 7;
			gaugeChart.addArrow(arrow);
			
			gaugeChart.write("chart__wind-speed");
			arrow.setValue(maxWindSpeed);

			axisMiles.bottomTextYOffset = -75;
			axisMiles.bottomTextColor = "#80a8d9";
			axisMiles.bottomTextBold = false;

			if (over) {
				label = '> ';
			}
			label += maxWindSpeed + " mi/h";

			axisMiles.setBottomText(label);
		});
	},
	_drawTempChart: function () {
		var chart;
		var chartData = [];

		AmCharts.ready(function () {
			// first we generate some random data
			generateChartData();

			// SERIAL CHART
			chart = new AmCharts.AmSerialChart();
			chart.dataProvider = chartData;
			chart.categoryField = "hours";

			// AXES
			// Category
			var categoryAxis = chart.categoryAxis;		 
			categoryAxis.gridAlpha = 0.07;
			categoryAxis.axisColor = "#DADADA";
			categoryAxis.labelFrequency = 2;
			categoryAxis.showLastLabel = true;
			categoryAxis.equalSpacing = true;

			// Value
			var valueAxis = new AmCharts.ValueAxis();
			valueAxis.gridAlpha = 0.07;
			
			chart.addValueAxis(valueAxis);

			// GRAPH
			var graph = new AmCharts.AmGraph();
			graph.type = "line"; // try to change it to "column"
			graph.title = "red line";
			graph.valueField = "grades";
			graph.lineAlpha = 1;
			graph.lineColor = "#d1cf2a";
			graph.fillAlphas = 0.3;
			graph.balloonText = "Temperature: [[grades]]&deg;F";
			
			chart.addGraph(graph);

			// CURSOR
			var chartCursor = new AmCharts.ChartCursor();
			chartCursor.cursorPosition = "mouse";
			chartCursor.zoomable = false;

			chart.addChartCursor(chartCursor);

			// WRITE
			chart.write("chart__feels-like");
		});

		// generate some random data, quite different range 
		function generateChartData() {
			$.each($('.weather__info-table-js tbody tr .weather__grades-max'), function (index, value) {
				chartData.push({
					grades: parseFloat($(value).attr('data-temp-grades')),
					hours:  $(value).attr('data-hour')
				});
			});
		}
	}
};

$(document).ready(function () {
	/* Remove unwanted stuff on mobile */
	if (isMobile.phone) {
		$('.hotel-photos .pure-g').remove();
		$('.place-photos .pure-g').remove();
		$('.pure-u-2-5.weather-panel').remove();
	}

	if (!isMobile.phone) {
		/* Load Weather Charts */
		Journal.plotWeatherCharts();
	}

	/* Get Map Information */
	var requests = [];

	var routeWaypoints = $.ajax({
		type: 'GET',
		url:  '/tj/search/places/' + $('#directions').attr('data-plan-id'),
		beforeSend: function () {

		},
		success: function (result) {
			Journal.places = result;
		},
		error: function () {

		}
	});
	requests.push(routeWaypoints);

	/* Initialize Map */
	var callback = function (results) {
		Journal.initMap();
	}

	$.when.all(requests).done(callback);

	/* Handle Profile Pictures */
	Journal.replaceProfileImages();

	/* Handle Background Pictures */
	Journal.replaceBackgroundImages();

	/* Handle Hotel Pictures */
	Journal.replaceHotelImages();

	/* Handle Place Photos */
	Journal.replacePlacesImages();

	/* Nifty Books */
	$('#books').on('click', '.js-modal', function () {
		$('#modal-content .md-wrapper').html($(this).find('.hidden-modal-content').html());
	});

	/* Nifty Youtube Videos */
	$('#videos').on('click', '.js-modal', function () {
		var $playerContainer = $(this).find('.video__popup-wrapper'),
			$playerObj = Journal.buildVideo($playerContainer.attr('data-video-id'));

		$playerContainer.append($playerObj);
		
		$('#modal-content .md-wrapper').html($playerContainer.parent().html());
	});

	/* Translate Review */
	$('.review-item').on('click', '.review-translate', function (e) {
		e.preventDefault();

		var $this = $(this),
			query = $this.prev('span').html();

		if (query) {
			$.ajax({
				type: 'POST',
				url:  '/api/google/translate',
				data: {
					q: query
				},
				beforeSend: function () {
				},
				success: function (result) {
					$this.fadeOut(200, function () {
						$this.prev('span').html(result);

						$this.parent().contents().filter(function () {
							return this.nodeType === 3;
						}).remove();
						
						$(this).remove();
					});
				},
				error: function () {
				}
			});
		}
	});
});
