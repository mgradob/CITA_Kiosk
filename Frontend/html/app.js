var main = function() {
	$('.button').click(function() {
		window.location.href = "menu_screen.html";
	});

	$('#solicitarBtn').click(function() {
		window.location.href = "solicitar.html";
	});

	$('.menu_element').click(function() {
		if ($(this).parent().hasClass('rent_type_menu')) {
			$('.rent_type_menu .menu_element_active').removeClass('menu_element_active');
			rentSelection = this.id;
			rent = true;
		} else if ($(this).parent().hasClass('zone_menu')) {
			$('.zone_menu .menu_element_active').removeClass('menu_element_active');
			zoneSelection = this.id;
			zone = true;
		};
		$(this).addClass('menu_element_active');
		enableBtn();
	});

	function enableBtn() {
		if (rent==true && zone==true) {
			console.log(rent);
			$('#nextBtn').removeClass('unabled_btn');
			$('#nextBtn').addClass('enabled_btn')
		};
	};

	$('#return_btn').click(function() {
		window.history.back();
	});

	$('#home_btn').click(function() {
		window.location.href = "index.html";
	});
};

$(document).ready(main);

/*$(document).on('click', '#solicitarBtn', function(){
		$('#menu').remove();
		$('#top').load('tags_directory.html #solicitar_locker');
	});*/