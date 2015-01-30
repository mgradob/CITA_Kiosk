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
				$('.modal-body').html($error);
                window.setTimeout(function(){window.location.href = "index.html";},3000);
				return;
			}
			$command = jsonMsg.command;
			$locker = jsonMsg.params.locker;
			$locker_id = jsonMsg.params.locker_id;
			$locker_confirmed = jsonMsg.params.locker_confirmado;
			$startDate = jsonMsg.params.inicio;
			$endDate = jsonMsg.params.entrega;
			$registered = jsonMsg.params.registrado;
			$type = jsonMsg.params.tipo;
			$userId = jsonMsg.params.matricula;
			$userName = jsonMsg.params.nombre;
			$bill = jsonMsg.params.pago;
			$area = jsonMsg.params.area;
			$.cookie('locker', $locker);
			$.cookie('locker_id', $locker_id);
			$.cookie('locker_confirmed', $locker_confirmed);
			$.cookie('startDate', $startDate);
			$.cookie('endDate', $endDate);
			$.cookie('registered', $registered);
			$.cookie('type', $type);
			$.cookie('userId', $userId);
			$.cookie('userName', $userName);
			$.cookie('bill', $bill);
			$.cookie('area', $area);
			//Si el usuario tiene locker asignado y la renta ha sido confirmada se va a la pantalla
			if ($registered == "True" && $locker_confirmed == "True"){
				window.location.href = "locker_asignado.html";
			}else{
				window.location.href = "menu_screen.html";
			};
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
			$.cookie('type', rentSelection);
			rent = true;
		} else if ($(this).parent().hasClass('zone_menu')) {
			$('.zone_menu .menu_element_active').removeClass('menu_element_active');
			zoneSelection = this.id;
			rentZone = document.getElementById(zoneSelection).innerHTML;
			$.cookie('area', rentZone);
			zone = true;
		};
		$(this).addClass('menu_element_active');
		enableBtn();
	});

	function on_btn_click(){

		if ($(this).parent().hasClass('rent_type_menu')) {
			$('.rent_type_menu .menu_element_active').removeClass('menu_element_active');
			rentSelection = this.id;
			$.cookie('type', rentSelection);
			rent = true;
		} else if ($(this).parent().hasClass('zone_menu')) {
			$('.zone_menu .menu_element_active').removeClass('menu_element_active');
			zoneSelection = this.id;
			rentZone = document.getElementById(zoneSelection).innerHTML;
			$.cookie('area', rentZone);
			zone = true;
		};
		$(this).addClass('menu_element_active');
		enableBtn();
	}

	/*funcion para habilitar botón siguiente*/
	function enableBtn() {
		if (typeof rent == "undefined") rent = false;
		if (typeof zone == "undefined") zone = false;

		if (rent==true && zone==true) {
			console.log(rent);
			$('#nextBtn').removeClass('unabled_btn');
			$('#nextBtn').addClass('enabled_btn');
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
				if ($command == "ERROR"){
				    $('#procesando').modal('hide');
                    $error = jsonMsg.params.description;
                    $('#modal_error_msg').html($error);
                    $('#modal_error').modal({
                        show: 'true',
                        backdrop: 'static',
                        keyboard:false
                    });
                    window.setTimeout(function(){$('#modal_error').modal('hide');},3000);
				    return;
				};
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

	/*funcion botón siguiente*/
	$('#pay_btn').click(function() {
        console.log("Pagando por Tiempo");
        window.location.href = "confirmar.html";
	});

	/*funcion para establecer valores de pantalla*/
	window.onload = function() {
		var command = $.cookie('command');

		if (typeof command == "undefined") command = "";
		else console.log(command);

		$('.subttitle').text("Bienvenido: " + $.cookie('userName'));
		$('.rent_user').text($.cookie('userId'));
		$('.rent_name').text($.cookie('userName'));
		$('.rent_start').text($.cookie('startDate'));

		$('.locker_id').text($.cookie('locker'));
		$('.zone_id').text($.cookie('area'));
		$('#total').html($.cookie('total'));

        console.log($.cookie('type'));
		if ($.cookie('type') == 'by_time') {
            $('#total').html($.cookie('bill'));

		    $('.rent_type').text('Renta por tiempo');
			$('#finish_date').addClass('hidden');
			$('.byTime_elements').removeClass('hidden');
			$('.cant_toPay').addClass('hidden');
			$('.confirm_button').removeClass('hidden');
			$('.start_payment').addClass('hidden');

			$('#elapsed_time').html(get_time_diff($.cookie('startDate')));
			$('#cant_toPay').html($.cookie('bill'));
			$('.rent_end').addClass('hidden');

		}else if ($.cookie('type') == 'by_semester') {
			$('.rent_type').text('Renta semestral');
            $('.finish_date').text(format_date($.cookie('endDate')));
			$('.byTime_elements').addClass('hidden');
			$('#finish_date').removeClass('hidden');
			$('.cant_toPay').removeClass('hidden');
			$('.confirm_button').addClass('hidden');
			$('.start_payment').removeClass('hidden');
			$('.rent_end').removeClass('hidden');
			$('#rent_end').html($.cookie('endDate'));
		};

        page = getPage();
        switch (page) {
            case "menu_screen.html":
                if($.cookie('locker_confirmed') == "False" && $.cookie('registered') == "True"){
                    alert("Proceso de reserva no completado");
                }
                break;
            case "cambiar.html":
                if ($.cookie('type') == 'by_time') {
                    $('#chUbic_btn').addClass('hidden');
                }
                break;
            case "confirmar.html":
                if($.cookie('locker_confirmed') == "True" && $.cookie('registered') == "True"){
                    $('.tittle').text('PAGO DEL LOCKER');
			        $('.cant_toPay').removeClass('hidden');
			        $('.change_btn').addClass('hidden');
			        $('.confirmBtn').addClass('hidden');
                }
                break;
        }
	};

	/*funcion para botón cambiar en pantalla confirmar*/
	$('.change_btn').click(function() {
		window.location.href = "cambiar.html";
	});

	// Función para botón sucio
	$('#dirty_btn').click(function() {
	    changeLockerStatus("is_dirty");
	});

	// Función para botón sucio
	$('#damaged_btn').click(function() {
	    changeLockerStatus("is_damaged");
	});

	function changeLockerStatus(new_status){
        $('#procesando').modal({
            show: 'true',
            backdrop: 'static',
            keyboard:false
        });
        var params = [$.cookie('locker_id'), new_status];
        sendMsg('CHANGE_LOCKER_STATUS', params);
        ws.onmessage = function(serverMsg) {
            console.log(serverMsg.data);
            mensaje = serverMsg.data;
            jsonMsg = JSON.parse(mensaje);
            $command = jsonMsg.command;
            switch($command){
                case "ERROR":
                    $error = jsonMsg.params.description;
                    $('#modal_error_msg').html($error);
				    $('#procesando').modal('hide');
                    $('#modal_error').modal({
                        show: 'true',
                        backdrop: 'static',
                        keyboard:false
                    });
                    window.setTimeout(function(){$('#modal_error').modal('hide');},3000);
                    break;
                case "CHANGED":
                    console.log(jsonMsg.params.locker_name);
                    console.log(jsonMsg.params.locker_id);
                    $.cookie('locker', jsonMsg.params.locker_name);
                    $.cookie('locker_id', jsonMsg.params.locker_id);
                    $('.locker_id').text(jsonMsg.params.locker_name);
				    $('#procesando').modal('hide');
                    break;
            };
        }
	}


    function getPage(){
        var path = window.location.pathname;
    	var page = path.split('/').pop();
    	return page;
    }

    function format_date(date){

        var m_names = new Array("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre",
            "Octubre", "Noviembre", "Diciembre");

        var d = new Date(date);
        var curr_date = d.getDate();
        var curr_month = d.getMonth();
        var curr_year = d.getFullYear();

        return curr_date + "-" + m_names[curr_month] + "-" + curr_year;
    }

    function get_time_diff( datetime )
    {
        var dtime = new Date( datetime );
        var ntime = new Date();

        var nTotalDiff = ntime.getTime() - dtime.getTime();
        var oDiff = new Object();

        oDiff.days = Math.floor(nTotalDiff/1000/60/60/24);
        nTotalDiff -= oDiff.days*1000*60*60*24;

        oDiff.hours = Math.floor(nTotalDiff/1000/60/60);
        nTotalDiff -= oDiff.hours*1000*60*60;

        oDiff.minutes = Math.floor(nTotalDiff/1000/60);

        // Calcular segundos
        //nTotalDiff -= oDiff.minutes*1000*60;
        //oDiff.seconds = Math.floor(nTotalDiff/1000);

        (oDiff.minutes > 0) ? extra = 1 : extra = 0;
        var totalHoras = oDiff.hours + extra;
        if (totalHoras >= 24) {
            oDiff.days += 1;
            totalHoras = 0;
        }

        var ret_string = totalHoras + " Horas "; // + oDiff.minutes + " Minutos";
        if (oDiff.days > 0){
            ret_string = oDiff.days + " Dias " + ret_string;
        }

        return ret_string;
    }

	/*función para el websocket*/
	$(document).ready( function () {
		if ("WebSocket" in window) {
            ws = new WebSocket("ws://localhost:1024");
            	page = getPage();
    			switch (page) {
    			    case "confirmar.html":
                        ws.onopen = function(event){
                            //Validar si es pago o no
                            prepare_payment();
                        };
                        break;
                    case "solicitar.html":
                        ws.onopen = function(event){
                            sendMsg('GET_AREAS');
                        }
                        break;
    			}
    			boolPaid = false;
            	ws.onmessage = function(serverMsg) {
            		console.log(serverMsg.data);
            		mensaje = serverMsg.data;
            		jsonMsg = JSON.parse(mensaje);
            		$command = jsonMsg.command;
    	    		switch ($command) {
    	    		    case 'AREAS':
    	    		        load_areas(jsonMsg["params"]["areas"]);
    	    		        break;
    	    		    case 'DEPOSIT':
                            $currentPay = jsonMsg.params.cantidad;
                            $('.payment').text($currentPay);
                            curPay = parseFloat($currentPay);
                            totPay = parseFloat($('#total').html());
                            if ((curPay >= totPay) && (!boolPaid)) {
                                $('#procesando').modal({
                                    show: 'true',
                                    backdrop: 'static',
                                    keyboard:false
                                });
                            };
                            break;
                        case 'PAID':
                            boolPaid = true;
                            $('#procesando').modal('hide');
                            $('#takeCard').modal('show');
                            window.setTimeout(function(){window.location.href = 'transaccion_exitosa.html'},3000);
                            break;
    	    		};	
            	};
        } else {
        	alert("WebSocket not supported");
    	};
	});

    function prepare_payment(){
        if ($.cookie('type') == 'by_time') {
            if($.cookie('locker_confirmed') == "True" && $.cookie('registered') == "True"){
                sendMsg('OK');
            }
        }else{
            sendMsg('OK');
        }
    }

    function deleteCookies(){
        $.removeCookie('userId');
        $.removeCookie('userName');
        $.removeCookie('locker');
        $.removeCookie('locker_id');
        $.removeCookie('locker_confirmed');
        $.removeCookie('registered');
        $.removeCookie('type');
        $.removeCookie('area');
        $.removeCookie('startDate');
        $.removeCookie('endDate');
        $.removeCookie('bill');
        $.removeCookie('total');
    }

    /* Displays the areas from the DB */
    function load_areas(jsonAreas){
        area = '';
        $.each(jsonAreas,function(i){
            area += '<li class="menu_element" id="' +  jsonAreas[i].area_id + '">' +
                jsonAreas[i].area_description + '</li><br/>'
        })
        $('.zone_menu').append(area);
        $('.menu_element').click(on_btn_click);
    }

	/* Web socket msg sender*/
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
	    deleteCookies();
		sendMsg('LOG_OUT');
		window.location.href = "index.html";
	});

	/*funcion de botón mi cuenta en menu principal*/
	$('#cuentaBtn').click(function() {
		window.location.href = "cuenta.html";
	});

	/*funcion de botón mi cuenta en menu principal*/
	$('#reportarBtn').click(function() {
		window.location.href = "cambiar.html";
	});

	/*funcion de botón back*/
	$('#return_btn').click(function() {
	    var page = getPage();
		switch(page){
            case "confirmar.html" :
			    $('#cancelar').modal('show');
			    //sendMsg('CANCEL');
			    break;
            case "locker_asignado.html":
                deleteCookies();
                window.history.back();
                break;
            default:
			    window.history.back();
		}
	});

	/*funcion de botón home*/
	$('#home_btn').click(function() {
	    deleteCookies();
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
