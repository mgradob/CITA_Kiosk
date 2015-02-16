# coding=utf-8
__author__ = 'mgradob'

from geventwebsocket import WebSocketServer, Resource, WebSocketApplication
from Utils import JsonMessages, ApiMessages, DataHolder
from Lockers import LockersSocket
from Lockers.Utils import Commands
import datetime
import time
import socket
import pytz
from VMC import VmcController
from Printer import PrinterController
from dateutil.parser import parse
import math


class EchoApplication(WebSocketApplication):
    """
    EchoApplication Class.
     A socket listening forever to the front-end, which will manage the vending services and the lockers.
    """

    locker = None
    user_in_session = None
    resend = False
    response, response_ant = '', ''

    card_key = ''
    locker_area_id = None
    av_locker = None

    vmc_start_flag = False
    socket_data_in = ''
    host_vmc, port_vmc = '127.0.0.1', 1025

    # Run a new thread of the VMC module.
    vmc = VmcController.VmcController(host_vmc, port_vmc, 1)
    vmc.start()

    # Run DataHolder thread.
    data_holder = DataHolder.DataHolder()
    data_holder.start()

    #Create a printer controller instance

    #printer = PrinterController.PrinterController('localhost', 1026, 2)
    #printer.start()

    # Open socket to the VMC Controller
    vmc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    printer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def on_open(self):
        """
        Initialization of the system (VMC, Websocket)
        """

        print 'Connection opened'

    def on_message(self, message):
        """
        When we receive a message from the front-end, call for the different services required.
        """

        # Validate for a valid message.
        if message is None:
            print 'Null message received'
        else:
            try:
                # Deserialize the command received.
                # Evaluate only the 'command' received.
                command = JsonMessages.Deserializer().get_command(message)
                print 'Received message: {}'.format(command)

                if command == 'READY':
                    # Frontend has connected to the socket.
                    # Send back the previous response command.
                    self.resend = True

                elif command == 'LOG_IN':
                    # Get user UID.
                    locker_socket = LockersSocket.LockerSocket()
                    self.card_key = locker_socket.send_command(Commands.Commands.read_key())[:8]
                    self.data_holder.card_key = self.card_key

                    if self.data_holder.card_key == "403":  # No hay tarjeta
                        print "No hay tarjeta"
                        self.response = JsonMessages.Error(True, "Tarjeta", "No hay tarjeta").get_json()
                    else:
                        try:
                            # Check for key existence in DB.
                            self.user_in_session = ApiMessages.User(self.data_holder.card_key).get_user()
                            assigned_locker = ApiMessages.Lockers().has_assigned_locker_info(self.data_holder.card_key)
                            str_locker_id = ''
                            str_locker_name = ''
                            str_locker_start = ''
                            str_locker_end = ''
                            str_locker_rent_type = ''
                            bol_registered = True
                            bol_locker_rent_confirmed = False
                            area_name = ''
                            payment = 0

                            if assigned_locker is None:
                                bol_registered = False
                            else:
                                str_locker_id = assigned_locker.locker_id
                                str_locker_name = assigned_locker.locker_name
                                bol_locker_rent_confirmed = assigned_locker.locker_rent_confirmed
                                str_locker_start = assigned_locker.locker_start_time
                                str_locker_end = assigned_locker.locker_end_time
                                str_locker_rent_type = assigned_locker.locker_rent_type
                                area = ApiMessages.Lockers().get_area_info(assigned_locker.fk_area)
                                self.data_holder.user_locker = assigned_locker

                                if area is not None:
                                    area_name = area.area_name
                                    self.data_holder.area_name = area_name
                                    self.data_holder.area_id = area.area_id

                            # Create Json response for the user.
                            user = '{} {} {}'.format(
                                self.user_in_session.user_name,
                                self.user_in_session.user_ap,
                                self.user_in_session.user_am
                            )

                            if str_locker_rent_type == 'by_time':
                                payment = self.calculate_payment(assigned_locker.locker_start_time, 0.4)
                                self.data_holder.total = payment
                                print payment

                            self.response = JsonMessages.User(
                                bol_registered,
                                str_locker_rent_type,
                                user,
                                self.user_in_session.user_mat,
                                str_locker_id,
                                str_locker_name,
                                bol_locker_rent_confirmed,
                                area_name,
                                str_locker_start,
                                str_locker_end,
                                payment
                            ).get_json()

                        except Exception as ex:
                            print ex
                            print "ERROR AL OBTENER USUARIO {}".format(self.card_key)
                            self.response = JsonMessages.Error(True, "Usuario",
                                                               "No se ha encontrado el usuario").get_json()

                elif command == 'GET_AREAS':
                    all_areas = ApiMessages.Lockers().get_areas_json()
                    self.response = JsonMessages.Areas(all_areas).get_json()

                    """
                        elif command == 'CHANGE_LOCKER_STATUS':
                        all_areas = ApiMessages.Lockers().get_areas_json()
                        self.response = JsonMessages.Areas(all_areas).get_json()
                    """

                    """
                    elif command == 'DELETE_USER':
                        print "USER TEST DELETE"
                        change_msg = JsonMessages.ChangeLockerStatus(message)
                        api_msg = ApiMessages.Lockers()
                        locker = api_msg.get_locker_info(change_msg.locker_id)
                        api_msg.test_delete_locker(locker)
                    """
                elif command == 'CHANGE_LOCKER_STATUS':
                    print "LOCKER CHANGE"
                    change_msg = JsonMessages.ChangeLockerStatus(message)
                    api_msg = ApiMessages.Lockers()
                    api_msg.change_locker_status(change_msg.locker_id, change_msg.status)
                    available_lockers = api_msg.get_available_lockers_area(self.data_holder.area_id)

                    if len(available_lockers) > 0:
                        print "DISPONIBLES PARA CAMBIO"
                        old_locker = self.data_holder.user_locker
                        new_locker = available_lockers[0]
                        api_msg.migrate_locker(old_locker, new_locker)

                        area = ApiMessages.Lockers().get_area_info(new_locker.fk_area)
                        self.data_holder.user_locker = new_locker
                        if area is not None:
                            area_name = area.area_name
                            self.data_holder.area_name = area_name
                            self.data_holder.area_id = area.area_id

                        self.response = JsonMessages.Changed(new_locker,area).get_json()
                        self.ws.send(self.response)

                        # TODO implement card
                    else:
                        print "SIN DISPONIBILIDAD"
                        self.response = JsonMessages.Error(
                            None, "NOT AVILABLE", "SIN DISPONIBILIDAD EN LA ZONA").get_json()
                        self.ws.send(self.response)
                    return
                elif command == 'SOLICIT':
                    # Create a Solicit message class, to easily handle message data.
                    # Create a Lockers message class.
                    solicit_msg = JsonMessages.Solicit(message)
                    api_msg = ApiMessages.Lockers()

                    try:
                        # Get the first available locker.
                        self.locker = api_msg.get_available_lockers_area(solicit_msg.area)[0]
                        self.data_holder.user_locker = self.locker

                        # Get the area_id of the selected locker.
                        for area in api_msg.areas_list:
                            if area.area_name == solicit_msg.area:
                                self.locker_area_id = area.area_id
                            else:
                                self.locker_area_id = '0'

                    except IndexError as ex:
                        print ex
                        print "SIN DISPONIBILIDAD"
                        self.response = JsonMessages.Error(None, "NOT AVAILABLE",
                                                           "SIN DISPONIBILIDAD EN LA ZONA").get_json()
                        self.ws.send(self.response)
                        return

                    except Exception as ex:
                        print ex
                        print "Error al solicitar"

                    # Check for rate type
                    if solicit_msg.tipo_cobro == 'by_semester':
                        fmt = '%Y-%m-%d %H:%M:%S'

                        # Get start and end dates.
                        date = datetime.datetime.now()
                        start_date = date.strftime(fmt)
                        end_date = str(datetime.datetime(2015, 06, 20, 0, 0, 0))
                        d1 = datetime.datetime.strptime(start_date, fmt)
                        # d2 = datetime.datetime.strptime('2015-06-20 00:00:00', fmt) # Replace with Semester date
                        #  Replace with Semester date
                        d2 = datetime.datetime.strptime(end_date, fmt)

                        # Convert to unix timestamp
                        d1_ts = time.mktime(d1.timetuple())
                        d2_ts = time.mktime(d2.timetuple())

                        # As a demo, payment is calculated by minute, on a standard rate ($0.005/min)
                        # They are now in seconds, subtract and then divide by 60 to get minutes.
                        minutes_to_pay = int(d2_ts-d1_ts) / 60
                        total = int(minutes_to_pay * 0.00002)  # Dummy rate
                        self.data_holder.total = total

                        # Assign the locker with the calculated pay.
                        api_msg.assign_locker(
                            self.data_holder.card_key,
                            self.data_holder.user_locker,
                            solicit_msg.tipo_cobro,
                            start_date, end_date
                        )

                        # Create Json response for confirmation.
                        self.response = JsonMessages.Confirm(
                            start_date, end_date,
                            self.data_holder.user_locker.locker_name,
                            total
                        ).get_json()
                        self.ws.send(self.response)

                    elif solicit_msg.tipo_cobro == 'by_time':
                        # Get start and end dates.
                        date = datetime.datetime.now() + datetime.timedelta(minutes=10)
                        start_date = date.strftime('%Y-%m-%d %H:%M:%S')

                        api_msg.assign_locker(
                            self.data_holder.card_key,
                            self.data_holder.user_locker,
                            solicit_msg.tipo_cobro,
                            start_date, None
                        )

                        # Create Json response for confirmation.
                        self.response = JsonMessages.Confirm(
                            inicio=start_date,
                            locker=self.data_holder.user_locker.locker_name,
                            total='TIME'
                        ).get_json()
                        self.ws.send(self.response)

                elif command == 'OK':
                    try:
                        sock_status = self.vmc_socket.connect_ex((self.host_vmc, self. port_vmc))
                        # Total a pagar en el monedero
                        self.vmc_socket.sendall('ACCEPT {}'.format(self.data_holder.total))
                        print "SOCKET STATUS {}".format(sock_status)

                    except Exception as ex:
                        print ex
                        print "Error al comunicar con el monedero 1"

                    try:
                        while True:
                            self.socket_data_in = self.vmc_socket.recv(1024)

                            if self.socket_data_in == 'CANCEL':
                                print "CANCELAR PEDIDO"
                                break
                            if self.socket_data_in == 'COMPLETE':
                                break
                            else:
                                balance = self.socket_data_in.split()[1]
                                print balance
                                self.response = JsonMessages.Deposit(balance).get_json()
                                self.ws.send(self.response)

                        response = LockersSocket.LockerSocket().send_command(
                            Commands.Commands.assign_access_level(
                                self.data_holder.user_locker.locker_name,
                                self.data_holder.card_key
                            )
                        )
                        print 'Assign access: {}'.format(response)

                        response = LockersSocket.LockerSocket().send_command(Commands.Commands.assign_new_key(
                            self.data_holder.card_key)
                        )
                        print 'Assign key: {}'.format(response)

                        # SAVE LOCKER CONFIRMATION
                        try:
                            ApiMessages.Lockers(self.data_holder.user_locker, True)
                        except Exception as ex:
                            print ex
                            print "ERROR AL CONFIRMAR LOCKER DESPUES DE PAGAR"

                        self.ws.send(JsonMessages.Paid().get_json())

                    except Exception as ex:
                        print ex
                        print "Error al comunicar con el monedero"

                elif command == 'ACCEPT':
                    # POR TIEMPO

                    LockersSocket.LockerSocket().send_command(
                        Commands.Commands.assign_by_time('')
                    )
                    print("PASO 1")

                    LockersSocket.LockerSocket().send_command(
                        Commands.Commands.assign_by_time2('')
                    )

                    print("PASO 2")

                    LockersSocket.LockerSocket().send_command(
                        Commands.Commands.update_key(self.data_holder.card_key)
                    )
                    print("PASO 3")
                    # print 'Assign access: {}'.format(response)

                    ApiMessages.Lockers(self.data_holder.user_locker, True)
                    self.ws.send(JsonMessages.Paid().get_json())

                elif command == 'CANCEL':
                    self.vmc_socket.sendall('CANCEL')
                    print 'Canceling'

                elif command == 'PRINT':
                    format_date = '%Y-%m-%d'
                    format_time = '%H:%M:%S'

                    # Get start and end dates.
                    date = datetime.datetime.now()
                    actual_date = date.strftime(format_date)
                    actual_time = date.strftime(format_time)

                    try:
                        #user_in_session : Info about user
                        #data_holder.user_locker : Info about locker
                        self.data_holder.folio += 1
                        number_of_zeroes = 7 - len(str(self.data_holder.folio))
                        folio = str(self.data_holder.folio).zfill(number_of_zeroes)
                        printer_status = self.printer_socket.connect_ex((self.host_vmc, 1026))
                        """self.printer_socket.sendall("{0}, {1},{2},{3},{4},{5},{6},{7},{8},{9}".format(command,
                                                    self.user_in_session.user_mat,folio, actual_date, actual_time,
                                                    self.data_holder.user_locker.locker_start_time,
                                                    self.data_holder.user_locker.locker_rent_type,
                                                    self.data_holder.user_locker.locker_name,
                                                    self.data_holder.area_name,self.data_holder.total,))"""
                        self.printer_socket.sendall("PRINT, MAT,FOLIO,"+actual_date+","+actual_time+",INICIO,ESQUEMA,LOCKER,A3,10")
                        print "PRINTER STATUS {}".format(printer_status)
                    except Exception as ex:
                        print ex
                        print "Error al comunicar con impresora"

                    print 'Printing ticket'

                elif command == 'LOG_OUT':
                    # TODO Implement logic for closing session.
                    print 'Login Out'

                else:
                    print "COMANDO NO SOPORTADO - {}".format(command)
                    self.response = 'Message not supported'

                # Save command, for posible future send backs.
                self.response_ant = self.response

                # Send the command.
                if self.resend:
                    self.ws.send(self.response_ant)
                else:
                    self.ws.send(self.response)

                print 'Answered: {}'.format(self.response)

            except Exception as ex:
                print ex
                self.response = JsonMessages.Error(True, "Otro", "Excepcion Generica").get_json()

    def calculate_payment(self, p_start, rate):
        payment = 0
        try:
            # Obtener la zona horaria de la maquina y añadirla a la hora actual
            str_timezone_diff = datetime.datetime.now(pytz.timezone('America/Chihuahua')).strftime('%z')
            end_time = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S{}".format(str_timezone_diff))

            # hacer un parse de las horas para verificar que estén en el formato adecuado
            start = parse(p_start)
            end = parse(end_time)

            # calcular el pago por ho
            # ra
            elapsed_time = end - start
            payment = math.ceil(elapsed_time.total_seconds()/60/60) * rate
        except Exception as ex:
            print ex
            print "ERROR AL CALCULAR PAGO"
            # self.response = JsonMessages.Error(True, "Calcular pago", "No se ha podido calcular el pago").get_json()
        return payment

    def on_close(self, reason):
        """
        When stopping the socket, we must check to stop all services.
        """
        print 'WebSocket closed\n{}'.format(reason)

"""
 Create a WebSocketServer, to listen to the front-end.
"""
WebSocketServer(
    ('127.0.0.1', 1024),  # Modify
    Resource({'/': EchoApplication})
).serve_forever()