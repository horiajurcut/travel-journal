$(document).ready(function() {
	$('.faq__item').not(':first').waypoint(function () {
		$(this).addClass('fade-in one');
	}, {
		offset: function () {
			return $.waypoints('viewportHeight') * 2 / 3;
		},
		context: window
	});
});