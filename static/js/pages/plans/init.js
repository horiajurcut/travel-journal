/* Poll for any Status change */
var Plans = {
	items: [],
	timer: null,
	favicon: null,
	badge: 0,
	statusChange: function () {
		$.ajax({ 
			url: '/tj/plans/status',
			success: function(data){
				if (data) {
					for (var i = 0; i < data.length; i++) {
						if (parseInt(data[i].plan_status, 10) !== 0) {
							var idx = Plans.items.indexOf(data[i].plan_id);
							if (idx != -1) {
								Plans.items.splice(idx, 1);
							}

							Plans.changeCard(data[i].plan_id);

							Plans.badge += 1;
							Plans.favicon.badge(Plans.badge);
						}
					}
				} else {
					if (Plans.timer) {
						clearTimeout(Plans.timer);
					}
				}
			},
			error: function(error) {
				if (Plans.timer) {
					clearTimeout(Plans.timer);
				}
			},
			type: "POST", 
			dataType: "json",
			data: {
				plans: Plans.items
			}, 
			complete: function () {
				if (Plans.items.length) {
					Plans.timer = setTimeout(Plans.statusChange, 10 * 1000);
				} else {
					$('.search').show();
				}
			}
		});
	},
	changeCard: function (plan_id) {
		var $item = $('.plan__card-item-js-' + plan_id);

		/* Remove Incomplete Block */
		$item.find('.plan__card-block-incomplete-js').remove();
		$item.find('.plan__card')
			.removeClass('incomplete')
			.addClass('new');

		/* Add New Block */
		var $ribbon = $(document.createElement('div'));

		$ribbon.addClass('plan__card-block')
			.append($(document.createElement('p')).text('NEW'))
			.append($(document.createElement('i')).addClass('fa fa-caret-down'));

		$item.find('.plan__card-title').append($ribbon);
	}
};

$(document).ready(function () {
	/* Load Favico */
	Plans.favicon = new Favico({
		animation : 'popFade'
	});

	/* List.js */
	if ($('.search').size()) {
		var options = {
			valueNames: [ 'js-city' ]
		};
		var featureList = new List('plans-wrapper', options);
		
		$('.search').on('keyup', function(){
			if (featureList.matchingItems.length < 1) {
				$('.plans__no-results').show();
			} else {
				$('.plans__no-results').hide();
			}
		});
	}

	/* Get all visible Plans */
	$.each($('.plans__items-list-js li'), function (index, value) {
		var plan_id = parseInt($(value).attr('data-plan-id'), 10),
			status = parseInt($(value).attr('data-status'), 10);
		
		if (plan_id && status === 0) {
			Plans.items.push(plan_id);
		}
	});

	/* Init Polling */
	if (Plans.items.length) {
		$('.search').hide();
		Plans.statusChange();
	}
});