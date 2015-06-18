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
			$balance = jsonMsg.params.balance;
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
			$.cookie('balance', $balance);
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

	/*funcion botón solicitar en menu principal*/
	$('#abonarBtn').click(function() {
		window.location.href = "abonar.html";
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
        moment.locale('es');
		var command = $.cookie('command');

		if (typeof command == "undefined") command = "";
		else console.log(command);

		$('.subttitle').text("Bienvenido: " + $.cookie('userName'));
		$('.rent_user').text($.cookie('userId'));
		$('.rent_name').text($.cookie('userName'));
		try{
		    rent_start = moment($.cookie('startDate')).format("DD/MMMM/YYYY hh:mm a");
		}catch(e){
            console.log(e);
            rent_start = "NONE";
		}
		$('.rent_start').text(rent_start);

		$('.locker_id').text($.cookie('locker'));
		$('.zone_id').text($.cookie('area'));
		$('#total').html($.cookie('total'));

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
			$('#user_balance').html($.cookie('balance'));
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

                    var now_m = moment();
                    var start_m = moment($.cookie('startDate'));
                    var start_p = moment($.cookie('startDate')).add(10, 'm');

                    if (moment(start_p).isBetween(start_m, now_m)){
                        // TODO eliminar confirmacion
                        //alert("Eliminar completado");
                        window.setTimeout(function(){makeLockerAvailable('available')}, 3000);
                    }else{
                        $('#confirmarBtn').removeClass('hidden');
                        alert("Proceso de reserva no completado");
                    }
                }
                $('#net_balance').html($.cookie('balance'));
                break;
            case "abonar.html":
                $('#net_balance').html($.cookie('balance'));
                break;
            case "cambiar.html":
                if ($.cookie('type') == 'by_time') {
                    $('#chUbic_btn').addClass('hidden');
                }
            //    break;
            // case "cambiar.html":
                $('.pay_done').addClass('hidden');
                $('.transactions').addClass('hidden');
                break;
            case "confirmar.html":
                $('.foot_btns button').addClass('hidden');
                if($.cookie('locker_confirmed') == "True" && $.cookie('registered') == "True"){
                    $('.tittle').text('PAGO DEL LOCKER');
			        $('.cant_toPay').removeClass('hidden');
			        $('.change_btn').addClass('hidden');
			        $('.confirmBtn').addClass('hidden');
			        $('.start_payment').removeClass('hidden');
                }
                if($.cookie('locker_confirmed') == "False" && $.cookie('type') == 'by_time'){
                    $('.total_cost').addClass('hidden');
                }
                break;
            case "transaccion_exitosa.html":
                var f_inicio = moment($.cookie('startDate')).format("DD - MMMM - YYYY hh:mm a");
                var f_fin = moment( $.cookie('endDate') );
                console.log(f_fin);
                console.log($.cookie('endDate'));
                (f_fin.isValid()) ? f_fin = f_fin.format("DD - MMMM - YYYY hh:mm a") : f_fin = "";

                $('#numeration').html();
                $('#user').html($.cookie('userId'));
                $('#start_date').html(f_inicio);
                $('#end_date').html(f_fin);
                $('#hour').html();
                $('#rent_type').html(rent_type_to_string($.cookie('type')));
                $('#locker').html($.cookie('locker'));
                $('#total').html($.cookie('total'));
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

	// Función para botón de cambio de locker
	$('#chUbic_btn').click(function() {
	    changeLockerStatus("is_relocated");
	});

	function makeLockerAvailable(new_status){

        var params = [$.cookie('locker_id'), new_status];
        sendMsg('MAKE_AVAILABLE', params);
	}


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

	// Función para botón de cambio de locker
	$('#detail_btn').click(function() {
	    $('#detail_text').html("");
        $('.transactions').text("0");
        $('.pay_done').text("0");
        $('#loader').removeClass('hidden');
        var params = [$.cookie('locker_id'), $('#month').val()];
        sendMsg('GET_LOG', params);
        ws.onmessage = function(serverMsg) {
            console.log(serverMsg.data);
            mensaje = serverMsg.data;
            jsonMsg = JSON.parse(mensaje);
            $command = jsonMsg.command;

            $('#loader').addClass('hidden');
            load_log(jsonMsg["params"]["logs"]);

        }
	});

    function rent_type_to_string (tipo){
        var tipoDeRenta = "";
        switch (tipo){
            case "by_semester":
                tipoDeRenta = "Renta por semestre";
            break;
            case "by_time":
                tipoDeRenta = "Renta por tiempo";
            break;
            case "locker_rent":
                tipoDeRenta = "Renta de locker";
            break;
        }
        return tipoDeRenta;
    }

    function load_log(jsonAreas){
        area = '';
        if (jsonAreas === undefined){
            area = '<div><p>NO HAY RESULTADOS</p>'
        }else{
            moment.locale('es');
            $('.pay_done').removeClass('hidden');
            $('.transactions').removeClass('hidden');
            total_pay = 0;
            $.each(jsonAreas, function(i){
                var f_inicio = moment(jsonAreas[i].log_start_time );
                var f_fin = moment(jsonAreas[i].log_end_time );
                (f_fin.isValid()) ? f_fin = f_fin.format("DD - MMMM - YYYY hh:mm a") : f_fin = "";

                area += '<div><p>Renta: <span class="log_detail">' + rent_type_to_string(jsonAreas[i].log_rent_type)
                    + "</span></p>" +
                    '<p>Inicio: <span class="log_detail">' + f_inicio.format("DD - MMMM - YYYY hh:mm a")+ '</span></p>' +
                    '<p>Fin: <span class="log_detail">' + f_fin + '</span></p>' +
                    '<p>Pagado: <span class="log_detail">' + jsonAreas[i].log_total_pay + '</span></p></div>';
                total_pay += jsonAreas[i].log_total_pay;
            });
            $('.transactions').text(jsonAreas.length);
            $('.pay_done').text(total_pay);

        }
        $('#detail_text').html(area);
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
    	    		    case 'DIFFERENCE':
                            $difference = jsonMsg.params.cantidad;
                            alert("Ha quedado saldo a su favor por una cantidad de " +  $difference);
                            /*$('.payment').text($currentPay);
                            curPay = parseFloat($currentPay);
                            totPay = parseFloat($('#total').html());
                            if ((curPay >= totPay) && (!boolPaid)) {
                                $('#procesando').modal({
                                    show: 'true',
                                    backdrop: 'static',
                                    keyboard:false
                                });
                            };*/
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
    	    		    case 'TIMEOUT':
			                $('#cancelarpago').modal('show');
			                /*
    	    		        if (confirm("¿Deseas seguir abonando?")){
	                            prepare_payment($currentPay);
    	    		        }
    	    		        else{
    	    		            alert("El saldo será abonado a tu cuenta");
    	    		            var old_balance = parseFloat($.cookie('balance'));
    	    		            sendMsg('ADD',[$currentPay - old_balance    ]);
    	    		        }*/
                            break;
                        case 'EXIT':
                            //boolPaid = true;
                            //$('#procesando').modal('hide');
                            //$('#takeCard').modal('show');
                            $('#msg_abono').html("Tu pago ha sido abonado");
                            window.setTimeout(function(){
                                    $('#modal_abono').modal('hide');

                                    if ($.cookie('type') == 'by_semester'){
                                        sendMsg('CANCEL');
                                    }
                                    window.location.href = 'index.html';
                                },2500);

                            //window.setTimeout(function(){window.location.href = 'transaccion_exitosa.html'},3000);
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

    function prepare_payment(current_balance){
        if (current_balance === undefined){
            current_balance = 0;
        }
        if ($.cookie('type') == 'by_time') {
            if($.cookie('locker_confirmed') == "True" && $.cookie('registered') == "True"){
                sendMsg('OK',['by_time', current_balance]);
            }
        }else{
            var user_balance= parseFloat($.cookie('balance'));
            var locker_total = parseFloat($.cookie('total'));
            if (user_balance > locker_total){
                if (confirm("El locker se pagará de su saldo")){
                    sendMsg('OK', [$.cookie('type'), current_balance]);
                }else{
                    sendMsg('CANCEL');
                    window.history.back();
                }
            }else{
                sendMsg('OK', [$.cookie('type'), current_balance]);
            }

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
        $('#loader').addClass('hidden');
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
		    window.location.href = "index.html";
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

	/* Funcion botón imprimir */
	$('#print_btn').click(function() {
        moment.locale('es');
        var f_inicio = moment($.cookie('startDate')).format("DD - MMMM - YYYY hh:mm a");
        var f_fin = moment( $.cookie('endDate') );
        var h_fin = "";

        if (f_fin.isValid()) {
            h_fin = f_fin.format("hh:mm a");
            f_fin = f_fin.format("DD - MMMM - YYYY");
        }else{
            f_fin = "";
        }

        $('#numeration').html();
        $('#rent_type').html();
        $('#locker').html();
        // User,
	    var params = [$.cookie('userId'), f_inicio, f_fin, h_fin, rent_type_to_string($.cookie('type')),
	        $.cookie('locker'), $('#total').html(), 001];
		sendMsg('PRINT', params);
		//window.location.href = "index.html";
	});

	/* Funcion botón de finalizar */
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
		window.location.href = "index.html";
	});

	/*contacto*/
	$('.contact').click(function() {
		$('#contact').modal('show');
	});

	$('#contact').click(function() {
		$('#contact').modal('hide');
	});

	/* cancelar */
	$('#sicancelar').click(function(){
	    var page = getPage();
		switch(page){
            case "confirmar.html" :
                if (($.cookie('type') == 'by_time') && ($.cookie('locker_confirmed')     == "False")){
                    $.cookie('locker', null);
                    $.cookie('endDate', null);
                    $.cookie('startDate', null);
                    $.cookie('bill', 0);
                    $.cookie('total', 0);
                }

			    break;
		}
        if (($.cookie('type') == 'by_time') && ($.cookie('locker_confirmed') == "False")){
		    sendMsg('CANCEL');
        }
		window.history.back();
	});

	/* cancelar */
	$('#sicancelarpago').click(function(){
	    prepare_payment($currentPay);
        $('#cancelarpago').modal('hide');
	});

	$('#nocancelarpago').click(function(){
        $('#msg_abono').html('"El saldo será abonado a tu cuenta"');
        $('#modal_abono').modal('show');
        //window.setTimeout(function(){$('#modal_abono').modal('hide');},3000);
        var old_balance = parseFloat($.cookie('balance'));
        sendMsg('ADD',[$currentPay - old_balance    ]);
	});
};

$(document).ready(main);
