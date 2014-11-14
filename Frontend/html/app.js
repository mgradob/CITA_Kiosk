var main = function() {

	/*funcion botón de inicio*/
	$('.button').click(function() {
		sendMsg('LOG_IN','');
		/*$.cookie('msg', 'cookie');
		window.location.href = "menu_screen.html";*/
		ws.onmessage = function(serverMsg) {
			console.log(serverMsg.data);
			mensaje = serverMsg.data;
			jsonMsg = JSON.parse(mensaje);
			$command = jsonMsg.command;
			$locker = jsonMsg.params.locker;
			$endDate = jsonMsg.params.entrega;
			$registred = jsonMsg.params.registrado;
			$type = jsonMsg.params.tipo;
			$userId = jsonMsg.params.matricula;
			$userName = jsonMsg.params.nombre;
			$bill = jsonMsg.params.pago;
			$area = jsonMsg.params.area;
			$.cookie('locker', $locker);
			$.cookie('endDate', $endDate);
			$.cookie('registred', $registred);
			$.cookie('type', $type);
			$.cookie('userId', $userId);
			$.cookie('userName', $userName);
			$.cookie('bill', $bill);
			$.cookie('area', $area);
			if ($registred == "True"){
				window.location.href = "locker_asignado.html";
			}else{
				window.location.href = "menu_screen.html";
			};
		}
		//window.location.href = "menu_screen.html";
	});

	/*funcion botón solicitar en menu principal*/
	$('#solicitarBtn').click(function() {
		window.location.href = "solicitar.html";
	});

	/*funcion elementos en menu de solicitar*/
	$('.menu_element').click(function() {
		if ($(this).parent().hasClass('rent_type_menu')) {
			$('.rent_type_menu .menu_element_active').removeClass('menu_element_active');
			rentSelection = this.id;
			console.log(rentSelection);
			rentArea = document.getElementById(rentSelection).innerHTML;
			console.log(rentArea);
			$.cookie('type', rentArea);
			rent = true;
		} else if ($(this).parent().hasClass('zone_menu')) {
			$('.zone_menu .menu_element_active').removeClass('menu_element_active');
			zoneSelection = this.id;
			console.log(zoneSelection);
			rentZone = document.getElementById(zoneSelection).innerHTML;
			console.log(rentZone);
			$.cookie('area', rentZone);
			zone = true;
		};
		$(this).addClass('menu_element_active');
		enableBtn();
	});

	/*funcion para habilitar botón siguiente*/
	function enableBtn() {
		if (rent==true && zone==true) {
			console.log(rent);
			$('#nextBtn').removeClass('unabled_btn');
			$('#nextBtn').addClass('enabled_btn')
		};
	};

	/*funcion botón siguiente*/
	$('#nextBtn').click(function() {
		if ($(this).hasClass('enabled_btn')) {
			var params = [rentSelection, zoneSelection]; 
			sendMsg('SOLICIT', params);
			ws.onmessage = function(serverMsg) {
				console.log(serverMsg.data);
				mensaje = serverMsg.data;
				jsonMsg = JSON.parse(mensaje);
				$command = jsonMsg.command;
				$locker = jsonMsg.params.locker;
				$endDate = jsonMsg.params.termino;
				$startDate = jsonMsg.params.inicio;
				$bill = jsonMsg.params.pago;
				$.cookie('locker', $locker);
				$.cookie('endDate', $endDate);
				$.cookie('startDate', $startDate);
				$.cookie('bill', $bill);
				window.location.href = "confirmar.html";
			};
		};
	});

	/*funcion para activar el web socket*/
	window.onload = function() {
		var command = $.cookie('command');
		console.log(command);
		console.log($.cookie('locker'));
		//console.log($.cookie('msg'));
		$('.subttitle').text("Bienvenido: " + $.cookie('userName'));
		$('.rent_type').text($.cookie('type'));
		$('.rent_user').text($.cookie('userId'));
		$('.rent_name').text($.cookie('userName'));
		$('.rent_start').text($.cookie('startDate'));
		$('.rent_end').text($.cookie('endDate'));
		$('.locker_id').text($.cookie('locker'));
		$('.zone_id').text($.cookie('area'));
		if ($.cookie('type') == 'TIME') {
			$('#finish_date').addClass('hidden');
			$('.byTime_elements').removeClass('hidden');	
		}else if ($.cookie('type') == 'SEMESTER') {
			$('.byTime_elements').addClass('hidden');
			$('#finish_date').removeClass('hidden');
		};
		if ("WebSocket" in window) {
            ws = new WebSocket("ws://10.33.17.61:49153");
        } else {
        	alert("WebSocket not supported");
    	};
    	ws.onmessage = function(serverMsg) {
    		console.log(serverMsg.data);
    		mensaje = serverMsg.data;
    		jsonMsg = JSON.parse(mensaje);
    		$command = jsonMsg.command;
    		if ($command == 'DEPOSIT') {
    			$currentPay = jsonMsg.params.cantidad;
    		}else if ($command == 'PAID') {
    			$('#takeCard').modal('show');
				window.setTimeout(function(){window.location.href = 'transaccion_exitosa.html'},3000);
    		};
    	};
	};

	/*funcion para botón cambiar en pantalla confirmar*/
	$('.change_btn').click(function() {
		window.location.href = "cambiar.html";
	});

	/*Simulación de monedero*/
	$payment = 0;
	document.onkeydown = function() {
		$payment = $payment + 10;
		console.log($payment);
		$('.payment').text($payment);
		$total = $('.total').text();
		if ($payment == $total) {
			//window.setTimeout(function(){$('#takeCard').modal('show')},2000);
    		$('#takeCard').modal('show');
			window.setTimeout(function(){window.location.href = 'transaccion_exitosa.html'},3000);
		}
	};

	/*Web socket msg sender*/
	function sendMsg(command, params) {
		var msg ={};
		msg['command'] = command;
		msg['params'] = params;
		var json = JSON.stringify(msg);
		console.log(json);
		ws.send(json);
	};

	/*funcion botón imprimir*/
	$('#print_btn').click(function() {
		sendMsg('PRINT');
		window.location.href = "index.html";
	});

	/*funcion botón de finalizar*/
	$('#endSesion_btn').click(function() {
		sendMsg('LOG_OUT');
		window.location.href = "index.html";
	});

	/*funcion de botón mi cuenta en menu principal*/
	$('#cuentaBtn').click(function() {
		window.location.href = "cuenta.html";
	});

	/*funcion de botón back*/
	$('#return_btn').click(function() {
		var path = window.location.pathname;
		var page = path.split('/').pop();
		if (page == "confirmar.html") {
			sendMsg('CANCEL');
		}
		window.history.back();
	});

	/*funcion de botón home*/
	$('#home_btn').click(function() {
		sendMsg('CANCEL');
		window.location.href = "index.html";
	});
};

$(document).ready(main);