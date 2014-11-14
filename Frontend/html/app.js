var main = function() {

	/*funcion botón de inicio*/
	$('.button').click(function() {
		sendMsg('LOG_IN','');
		//window.location.href = "menu_screen.html";
		ws.onmessage = function(serverMsg) {
			console.log(serverMsg.data);
			mensaje = serverMsg.data;
			ws.close();
			window.location.href = "menu_screen.html";
		}
	
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
			rent = true;
		} else if ($(this).parent().hasClass('zone_menu')) {
			$('.zone_menu .menu_element_active').removeClass('menu_element_active');
			zoneSelection = this.id;
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
			window.location.href = "confirmar.html";
		}
	});

	/*funcion para activar el web socket*/
	window.onload = function() {
		if ("WebSocket" in window) {
            ws = new WebSocket("ws://localhost:49153");
            //sendMsg('READY','');
            /*ws.onmessage = function (msg) {
            	var server_msg = msg.data;
        		/*var hear_msg = JSON.parse(msg);
        		var command = hear_msg.command;
        		var params = hear_msg.params;
        		/*switch (command) {
        			case 'USER'
	        			$register = params[1];
	        			$type = params[2];
	        			$name = params[3];
	        			$id = params[4];
	        			$locker = params[5];
	        			$area = params[6];
	        			$finish_date = params[7];
	        			$balance = params[8];
	        			break;
	        		case 'CONFIRM'
	        			$start_date = hear_msg.params[1];
	        			$end_date = hear_msg.params[2];
	        			$locker = hear_msg.params[3];
	        			$area = hear_msg.params[4];
	        			$total = hear_msg.params[5];
	        			break;
	        		case 'DEPOSIT'
	        			$cant = hear_msg.params[1];
	        			break;
	        		case 'PAID'
	        			break;
        		}*/
        		//console.log(server_msg);
        		
			//};
        } else {
        	alert("WebSocket not supported");
    	}
    	console.log(mensaje);
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
			window.location.href = 'transaccion_exitosa.html';
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
		/*ws.onopen = function() {
			ws.send(json);
		};*/
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

/*$(document).on('click', '#solicitarBtn', function(){
		$('#menu').remove();
		$('#top').load('tags_directory.html #solicitar_locker');
	});*/