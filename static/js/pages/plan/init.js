$(document).ready(function() {
	/* Pick a Date */
	$('.datepicker').pickadate({
		min: true,
		max: 365,
		weekdaysShort: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'],
		showMonthsShort: true,
		onClose: function() {
			$('.datepicker').blur();
		},
		format: 'dddd, dd mmm, yyyy',
		formatSubmit: 'yyyy-mm-dd'
	});

	/* Typeahead */
	$('.typeahead').typeahead({
		name: 'places',
		remote: '/api/google/places/autocomplete?q=%QUERY'
	});

	$('.typeahead').bind('typeahead:selected', function(obj, datum, name) {
		var geocoder = new google.maps.Geocoder(),
			location = null,
			components = null,
			country = null,
			city = null,
			city_backup = null;
		
		geocoder.geocode({ 'address': datum.value }, function (results, status) {
			if (status == google.maps.GeocoderStatus.OK) {
				location = results[0].geometry.location;
				components = results[0].address_components;

				for (var i = 0; i < components.length; i++) {
					var item = components[i].types;
					for (var j = 0; j < item.length; j++) {
						if (item[j] === 'country') {
							country = components[i].short_name;
						}

						if (item[j] === 'locality') {
							city = components[i].long_name;
						}

						if (item[j] === 'administrative_area3') {
							city_backup = components[i].long_name;
						}
					}
				}

				$('#latitude').val(location.lat());
				$('#longitude').val(location.lng());

				if (country) {
					$('#country').val(country);
				}

				if (city_backup && !city) {
					$('#short_city').val(city_backup);
				}

				if (city) {
					$('#short_city').val(city);
				}
			} else {
				console.log('Geocode was not successful for the following reason: ' + status);
			}
		});
	});

	/* Validate Plan Form */
	$('#plan__trip').submit(function (e) {
		if (!$('#city').val()) {
			$('.q-location-js').addClass('required-question');
			$('#city').addClass('required');
			
			e.preventDefault();
			return;
		} else {
			$('.q-location-js').removeClass('required-question');
			$('#city').removeClass('required');
		}

		if (!$('#future_day').val()) {
			$('.q-day-js').addClass('required-question');
			$('#future_day').addClass('required');

			e.preventDefault();
			return;
		} else {
			$('.q-day-js').removeClass('required-question');
			$('#future_day').removeClass('required');
		}

		if ($('#places__container-checkboxes-js').find('input[type=checkbox]:checked').length == 0) {
			$('.q-places-js').addClass('required-question');
			
			e.preventDefault();
			return;
		} else {
			$('.q-places-js').removeClass('required-question');
		}

		if ($('#events__container-checkboxes-js').find('input[type=checkbox]:checked').length == 0) {
			$('.q-events-js').addClass('required-question');
			
			e.preventDefault();
			return;
		} else {
			$('.q-events-js').removeClass('required-question');
		}

		return;
	});
});