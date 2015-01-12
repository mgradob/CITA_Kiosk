var main = function() {

	/*funcion botón de inicio*/
	$('.button').click(function() {
        sendMsg('LOG_IN','');
		$('#procesando').modal({
			show: 'true',
			backdrop: 'static',
			keyboard:false
		});
		ws.onmessage = function(serverMsg) {
			$('#procesando').modal({
				show: 'false',
				backdrop: true,
			});
			console.log(serverMsg.data);
			mensaje = serverMsg.data;
			jsonMsg = JSON.parse(mensaje);
			if(jsonMsg.params.abort == "True"){
				$error = jsonMsg.params.description;
				$('.modal-body').html($error)
				window.location.href = "index.html";
				return
			}
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
		if (typeof rent == "undefined") rent = false;
		if (typeof zone == "undefined") zone = false;

		if (rent==true && zone==true) {
			console.log(rent);
			$('#nextBtn').removeClass('unabled_btn');
			$('#nextBtn').addClass('enabled_btn')
		};
	};

	/*funcion botón siguiente*/
	$('#nextBtn').click(function() {
		if ($(this).hasClass('enabled_btn')) {
			$('#procesando').modal({
                show: 'true',
                backdrop: 'static',
                keyboard:false
            });
            console.log("Solicitando Locker");
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
				$total = jsonMsg.params.total;
				$.cookie('locker', $locker);
				$.cookie('endDate', $endDate);
				$.cookie('startDate', $startDate);
				$.cookie('bill', $bill);
				$.cookie('total', $total);
				window.location.href = "confirmar.html";
			};
		};
	});

	/*funcion para establecer valores de pantalla*/
	window.onload = function() {
		var command = $.cookie('command');
		if (typeof command == "undefined") command = "";
		console.log(command);
		console.log($.cookie('locker'));
		$('.subttitle').text("Bienvenido: " + $.cookie('userName'));
		$('.rent_type').text($.cookie('type'));
		$('.rent_user').text($.cookie('userId'));
		$('.rent_name').text($.cookie('userName'));
		$('.rent_start').text($.cookie('startDate'));
		$('.rent_end').text($.cookie('endDate'));
		$('.locker_id').text($.cookie('locker'));
		$('.zone_id').text($.cookie('area'));
		$('.total').text($.cookie('total'))
		if ($.cookie('type') == 'Por tiempo') {
			$('#finish_date').addClass('hidden');
			$('.byTime_elements').removeClass('hidden');
			$('.cant_toPay').addClass('hidden');
			$('.confirm_button').removeClass('hidden');
			$('.start_payment').addClass('hidden');
			$('.total_cost').text("Cuota: $")
		}else if ($.cookie('type') == 'Semestral') {
			$('.byTime_elements').addClass('hidden');
			$('#finish_date').removeClass('hidden');
			$('.cant_toPay').removeClass('hidden');
			$('.confirm_button').addClass('hidden');
			$('.start_payment').removeClass('hidden');
		};
	};

	/*funcion para botón cambiar en pantalla confirmar*/
	$('.change_btn').click(function() {
		window.location.href = "cambiar.html";
	});

	/*función para el websocket*/
	$(document).ready( function () {
		if ("WebSocket" in window) {
            ws = new WebSocket("ws://localhost:1024");
            	var path = window.location.pathname;
    			var page = path.split('/').pop();
    			if (page == "confirmar.html") {
    				ws.onopen = function(event){
                        if ($.cookie('type') == 'Por tiempo') {

                        }else{
    					    sendMsg('OK');
    					}
    				};
    			}
    			boolPaid = false;
            	ws.onmessage = function(serverMsg) {
            		console.log(serverMsg.data);
            		mensaje = serverMsg.data;
            		jsonMsg = JSON.parse(mensaje);
            		$command = jsonMsg.command;
    	    		if ($command == 'DEPOSIT') {
    	    			$currentPay = jsonMsg.params.cantidad;
    	    			$('.payment').text($currentPay);
    	    			curPay = parseFloat($currentPay);
    	    			totPay = parseFloat($('.total').text());
    	    			if ((curPay >= totPay) && (!boolPaid)) {
    	    			    $('#procesando').modal({
    	    					show: 'true',
    	    					backdrop: 'static',
    	    					keyboard:false
    	    				});
    	    			};
    	    		}else if ($command == 'PAID') {
    	    		    boolPaid = true;
    	    			$('#procesando').modal('hide');
    	    			$('#takeCard').modal('show');
    					window.setTimeout(function(){window.location.href = 'transaccion_exitosa.html'},3000);
    	    		};	
            	};
        } else {
        	alert("WebSocket not supported");
    	};
	});

	/*Web socket msg sender*/
	function sendMsg(command, params) {
		var msg ={};
		msg['command'] = command;
		msg['params'] = params;
		var json = JSON.stringify(msg);
		console.log(json);
		try{
		    ws.send(json);
		}
		catch(err) {
            console.log(err.message);
            alert("ERROR DE SOCKET");
            return;
        }
	};

	/*función para botón de confirmar renta (modalidad tiempo)*/
	$('.confirmBtn').click(function() {
		sendMsg('ACCEPT');
		$('#procesando').modal({
			show: 'true',
			backdrop: 'static',
			keyboard:false
		});
	});

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
			$('#cancelar').modal('show');
			//sendMsg('CANCEL');
		}else{
			window.history.back();
		}
	});

	/*funcion de botón home*/
	$('#home_btn').click(function() {
		sendMsg('CANCEL');
		window.location.href = "index.html";
	});

	/*contacto*/
	$('.contact').click(function() {
		$('#contact').modal('show');
	});

	$('#contact').click(function() {
		$('#contact').modal('hide');
	});

	/*cancelar*/
	$('#sicancelar').click(function(){
		sendMsg('CANCEL');
		window.history.back();
	});
};

$(document).ready(main);
