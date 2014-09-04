$(document).ready(function() {
	$('.box-wrapper').not(':first').waypoint(function () {
		$(this).addClass('fade-in one');
	}, {
		offset: function () {
			return $.waypoints('viewportHeight') * 2 / 3;
		},
		context: window
	});


	var $this = $('.header-image'), 
		$background = $(document.createElement('img'));

	$background
		.load(function () {
			$this.attr('style', 'background-image: url(' + $this.attr('data-background-img') + ');');
			$this.addClass('fade-in one');
			$(this).remove();
		})
		.error(function () {
			console.log('Image not found on Flickr Servers');
		})
		.attr('src', $this.attr('data-background-img'));
});