# coding=utf-8
__author__ = 'mgradob','luishoracio'

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

    # Create a printer controller instance

    printer = PrinterController.PrinterController('localhost', 1026, 2)
    printer.start()

    # Open socket to the VMC Controller
    vmc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    printer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def on_open(self):
        """
        Initialization of the system (VMC, Websocket)
        """

        print 'Connection opened'

    def on_message(self, message, **kwargs):
        """
        When we receive a message from the front-end, call for the different services required.
        :param **kwargs:
        :param message:
        :type self: object
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
                    if self.card_key == "ERRSALTO":
                        self.response = JsonMessages.Error(True, "Salto",
                                                           "Error de comunicación con SALTO").get_json()
                        self.ws.send(self.response)
                        return
                    # If there's no card
                    if self.data_holder.card_key == "403":
                        print "NO CARD"
                        self.response = JsonMessages.Error(True, "Tarjeta", "No hay tarjeta").get_json()
                    else:
                        try:
                            # Check for key existence in DB.
                            self.user_in_session = ApiMessages.User(self.data_holder.card_key).get_user()
                            self.data_holder.user = self.user_in_session
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
                            balance = float(self.user_in_session.user_balance)
                            self.data_holder.balance = balance
                            self.get_rates()

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
                            # if the rent is by time, calculate the payment
                            self.data_holder.rent_type = str_locker_rent_type
                            if str_locker_rent_type == 'by_time':
                                payment = self.calculate_payment(assigned_locker.locker_start_time)
                                self.data_holder.total = payment
                                date = datetime.datetime.now()
                                str_locker_end = date.strftime('%Y-%m-%d %H:%M:%S')
                                self.data_holder.end_date = str_locker_end
                                print payment

                            # TODO Set locker free if it's not confirmed after X time

                            # if it's by semester, check if the
                            elif str_locker_rent_type == 'by_semester':
                                fmt2 = '%Y-%m-%dT%H:%M:%SZ'
                                end_date = datetime.datetime.strptime(assigned_locker.locker_end_time, fmt2)

                                # check if locker ran out of time. Doesn't save end date
                                if end_date < datetime.datetime.now():
                                    ApiMessages.Lockers().set_locker_available(assigned_locker)
                                    str_locker_id = ''
                                    str_locker_name = ''
                                    bol_locker_rent_confirmed = False
                                    bol_registered = False
                                    area_name = ''
                                    payment = 0
                                    print "RAN OUT OF TIME"
                                else:
                                    # Save end date into dataholder
                                    fmt3 = '%Y-%m-%dT%H:%M:%SZ'
                                    end_date2 = datetime.datetime.strptime(assigned_locker.locker_end_time, fmt3)
                                    str_locker_end = end_date2.strftime('%Y-%m-%d %H:%M:%S')
                                    print "{} - {}".format(end_date2, str_locker_end)
                                    self.data_holder.end_date = str_locker_end

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
                                payment,
                                balance
                            ).get_json()

                        except Exception as ex:
                            print "ERROR AL OBTENER USUARIO {} - {}".format(self.card_key, ex)
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
                # Command to change the locker into available status
                elif command == 'MAKE_AVAILABLE':
                    print "MAKE LOCKER AVAILABLE"
                    change_msg = JsonMessages.ChangeLockerStatus(message)
                    api_msg = ApiMessages.Lockers()
                    api_msg.make_locker_available(change_msg.locker_id)
                    return

                # Command to change the locker due to dirt or failure
                elif command == 'CHANGE_LOCKER_STATUS':
                    print "LOCKER CHANGE"
                    change_msg = JsonMessages.ChangeLockerStatus(message)
                    api_msg = ApiMessages.Lockers()
                    available_lockers = api_msg.get_available_lockers_area(self.data_holder.area_id)

                    # Check for some available lockers
                    if len(available_lockers) > 0:
                        api_msg.change_locker_status(change_msg.locker_id, change_msg.status)
                        old_locker = api_msg.get_locker_info(change_msg.locker_id)

                        print "LOCKERS AVAILABLE FOR SWAP"

                        new_locker = available_lockers[0]
                        api_msg.migrate_locker(old_locker, new_locker)

                        area = ApiMessages.Lockers().get_area_info(new_locker.fk_area)
                        self.data_holder.user_locker = new_locker
                        if area is not None:
                            area_name = area.area_name
                            self.data_holder.area_name = area_name
                            self.data_holder.area_id = area.area_id

                        if change_msg.status == 'is_relocated':
                            api_msg.set_locker_available(old_locker)

                        now_plus_10 = datetime.datetime.today() + datetime.timedelta(minutes=10)

                        if self.data_holder.rent_type == 'by_semester':
                            new_end_date = self.data_holder.end_date
                            fmt3 = '%Y-%m-%d %H:%M:%S'
                            end_date2 = datetime.datetime.strptime(new_end_date, fmt3)
                            print "new date semester: {}". format(end_date2)
                            self.program_card(self.data_holder.card_key,
                                               self.data_holder.user_locker.locker_name,
                                               end_date2)

                        elif self.data_holder.rent_type == 'by_time':
                            print "new date time: {}". format(now_plus_10)
                            if now_plus_10.minute % 10 > 5:
                                new_end_date = now_plus_10 + datetime.timedelta(minutes=10)
                                print "Diez minutos más"
                            else:
                                new_end_date = now_plus_10
                            self.program_two_cards(self.data_holder.card_key,
                                                   old_locker.locker_name,
                                                   self.data_holder.user_locker.locker_name,
                                                   new_end_date)

                        self.response = JsonMessages.Changed(new_locker, area).get_json()
                        self.ws.send(self.response)


                    else:
                        print "SIN DISPONIBILIDAD"
                        self.response = JsonMessages.Error(
                            None, "NOT AVAILABLE", "SIN DISPONIBILIDAD EN LA ZONA").get_json()
                        self.ws.send(self.response)
                        return

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
                        print "SIN DISPONIBILIDAD - {}".format(ex)
                        self.response = JsonMessages.Error(None, "NOT AVAILABLE",
                                                           "SIN DISPONIBILIDAD EN LA ZONA").get_json()
                        self.ws.send(self.response)
                        return

                    except Exception as ex:
                        print "Error al solicitar {}".format(ex)

                    # Check for rate type
                    if solicit_msg.tipo_cobro == 'by_semester':
                        self.data_holder.rent_type = 'by_semester'
                        fmt = '%Y-%m-%d %H:%M:%S'

                        # Get start and end dates.
                        date = datetime.datetime.now()
                        start_date = date.strftime(fmt)

                        per_msg = ApiMessages.Periods()

                        end_date = start_date
                        bool_first = True
                        aux_period = None
                        for period in per_msg.periods_list:

                            fmt2 = '%Y-%m-%dT%H:%M:%SZ'
                            aux_start_time = datetime.datetime.strptime(period.period_start_time, fmt2)
                            aux_end_time = datetime.datetime.strptime(period.period_end_time, fmt2)
                            print "aux1 - {}".format(aux_end_time)

                            if date.date() < aux_start_time.date() or date.date() > aux_end_time.date():
                                print "Menor o mayor"
                            else:
                                if bool_first:
                                    bool_first = False
                                    end_date = aux_end_time
                                    aux_period = period
                                    print "X1"
                                else:
                                    if aux_end_time.date() < end_date.date():
                                        end_date = aux_end_time
                                        aux_period = period

                        if bool_first:
                            print "SIN PERIODOS"
                            self.response = JsonMessages.Error(None, "NOT AVAILABLE",
                                                               "NO HAY PERIODOS DISPONIBLES").get_json()
                            self.ws.send(self.response)
                            return

                        d1 = datetime.datetime.strptime(start_date, fmt)
                        d2 = end_date

                        # Convert to unix timestamp
                        d1_ts = time.mktime(d1.timetuple())
                        d2_ts = time.mktime(d2.timetuple())

                        # As a demo, payment is calculated by minute, on a standard rate ($0.005/min)
                        minutes_to_pay = int(d2_ts - d1_ts) / 60
                        hours_to_pay = minutes_to_pay / 60
                        total = int(hours_to_pay * self.data_holder.rate_s)
                        print "horas: {}, rate: {}, rawTotal: {}".format(hours_to_pay,
                                                                         self.data_holder.rate_s,
                                                                         hours_to_pay * self.data_holder.rate_s)
                        self.data_holder.total = total
                        self.data_holder.end_date = end_date

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
                            total, aux_period.period_name
                        ).get_json()
                        self.ws.send(self.response)

                    elif solicit_msg.tipo_cobro == 'by_time':
                        self.data_holder.rent_type = 'by_time'

                        # Get start and end dates.
                        date = datetime.datetime.now()  # + datetime.timedelta(minutes=10)
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
                            total='APARTADO',
                            periodo=None
                        ).get_json()
                        self.ws.send(self.response)

                elif command == 'OK':
                    ok_msg = JsonMessages.OkAvailable(message)
                    print "NUEVO SALDO - {}".format(ok_msg.added_payment)

                    new_added = float(ok_msg.added_payment)

                    if new_added > 0:
                        new_added -= float(self.data_holder.balance)

                    current_user_balance = float(self.data_holder.balance) + new_added
                    amount_to_pay = float(self.data_holder.total)
                    pay_completed = False
                    try:
                        # CONNECT TO VMC SOCKET
                        sock_status = self.vmc_socket.connect_ex((self.host_vmc, self.port_vmc))

                        if self.data_holder.rent_type == 'by_semester':
                            print "SEMESTER - USER WILL PAY {}".format(amount_to_pay)

                        amount_to_pay -= float(self.data_holder.balance)
                        print "Total: {} - user balance: {} - total: {}".format(self.data_holder.total,
                                                                                current_user_balance,
                                                                                amount_to_pay)
                        if amount_to_pay <= 0:
                            pay_completed = True
                            self.response = JsonMessages.Deposit(current_user_balance).get_json()
                            self.ws.send(self.response)
                            ApiMessages.User().set_user_balance(self.data_holder.card_key, abs(amount_to_pay))
                        else:
                            self.response = JsonMessages.Deposit(current_user_balance).get_json()
                            self.ws.send(self.response)
                            # SEND TOTAL AMOUNT TO PAY
                            self.vmc_socket.sendall('ACCEPT {}'.format(amount_to_pay))
                            print "SOCKET STATUS {}".format(sock_status)

                            # LISTEN TO THE VMC PAYMENT
                            try:
                                while True:
                                    self.socket_data_in = self.vmc_socket.recv(1024)

                                    if self.socket_data_in == 'CANCEL':
                                        print "CANCELAR PEDIDO"
                                        break

                                    if self.socket_data_in == 'COMPLETE':
                                        pay_completed = True
                                        break
                                    else:
                                        comando = self.socket_data_in.split()[0]
                                        balance = float(self.socket_data_in.split()[1]) + current_user_balance

                                        if comando == 'DIFFERENCE':
                                            ApiMessages.User().set_user_balance(self.data_holder.card_key, balance)
                                            self.response = JsonMessages.Difference(balance).get_json()
                                        elif comando == 'TIMEOUT':
                                            self.response = JsonMessages.Timeout(balance).get_json()
                                            break
                                        else:
                                            self.response = JsonMessages.Deposit(balance).get_json()

                                        self.ws.send(self.response)

                                # TODO SI QUEDA CAMBIO
                                # ApiMessages.User().set_user_balance(self.data_holder.card_key, abs(**CAMBIO**))

                            except Exception as ex:
                                print "ERROR AL PAGAR EN EL MONEDERO {}".format(ex)

                    except Exception as ex:
                        print "ERROR AL COMUNICAR CON EL MONEDERO - {}".format(ex)

                    if pay_completed:
                        new_end_date = datetime.datetime.today() + datetime.timedelta(minutes=10)

                        if self.data_holder.rent_type == 'by_time':
                            print "USER PAID RENT BY TIME"

                        elif self.data_holder.rent_type == 'by_semester':
                            print "USER PAID BY SEMESTER"
                            new_end_date = self.data_holder.end_date
                        else:
                            print "OTRO"

                        if new_end_date.minute % 10 > 5:
                            new_end_date = new_end_date + datetime.timedelta(minutes=10)
                            print "Diez minutos más"

                        print "{}".format(new_end_date)
                        self.program_card(self.data_holder.card_key,
                                          self.data_holder.user_locker.locker_name,
                                          new_end_date)

                        api_msg = ApiMessages.Lockers()

                        # SAVE LOCKER CONFIRMATION
                        if ok_msg.rent_type == 'by_semester':
                            api_msg.confirm_assign_locker(self.data_holder.user_locker, True)
                        elif ok_msg.rent_type == 'by_time':
                            #api_msg.confirm_assign_locker(self.data_holder.user_locker, True) #Cambiado el 16/Junio/15 #No funcionó
                            api_msg.set_locker_available(self.data_holder.user_locker)

                        # RETURN PAID MESSAGE TO FRONTEND
                        self.ws.send(JsonMessages.Paid().get_json())

                        # RECORD LOG
                        api_msg.locker_paid(self.data_holder.user_locker, self.data_holder.card_key,
                                            self.data_holder.total, ok_msg.rent_type, self.data_holder.end_date)


                elif command == 'ADD':
                    get_log_msg = JsonMessages.GetMoney(message)
                    # print "{}".format(new_msg.user_balance)
                    print "{}".format(get_log_msg.command)
                    new_balance = float(self.data_holder.user.user_balance) + float(get_log_msg.cantidad)
                    ApiMessages.User().set_user_balance(self.data_holder.card_key, new_balance )

                    self.ws.send(JsonMessages.Exit().get_json())
                    return
                elif command == 'ACCEPT':
                    print "USER RENTED BY TIME"

                    new_end_date = datetime.datetime.today() + datetime.timedelta(minutes=10)

                    if new_end_date.minute % 10 > 5:
                        new_end_date = new_end_date + datetime.timedelta(minutes=10)
                        print "PLUS 10 MINUTES"

                    self.program_card(self.data_holder.card_key,
                                      self.data_holder.user_locker.locker_name,
                                      new_end_date)

                    api_msg = ApiMessages.Lockers(self.data_holder.user_locker, True)
                    self.ws.send(JsonMessages.Paid().get_json())
                    print "{} - ".format(self.data_holder.user_locker.locker_start_time)
                    api_msg.locker_paid(self.data_holder.user_locker, self.data_holder.card_key,
                                        0, "locker_rent", None)

                elif command == 'GET_LOG':
                    get_log_msg = JsonMessages.GetLog(message)
                    print "{} - {}".format(self.data_holder.card_key, get_log_msg.month)
                    msg_log = ApiMessages.Log(self.data_holder.card_key)
                    logs = msg_log.get_log(get_log_msg.month)

                    if len(logs) > 0:
                        self.ws.send(JsonMessages.Logs(logs).get_json())
                    else:
                        print "SIN LOGS"
                        self.response = JsonMessages.Error(None, "NOT AVAILABLE",
                                                           "NO HAY TRANSACCIONES DISPONIBLES").get_json()
                        self.ws.send(self.response)
                    return

                elif command == 'CANCEL':
                    print 'Canceling'
                    api_msg = ApiMessages.Lockers()
                    api_msg.set_locker_available(self.data_holder.user_locker)
                    self.data_holder.user_locker = None

                elif command == 'PRINT':
                    get_print_msg = JsonMessages.Print(message)
                    # format_date = '%Y-%m-%d'
                    # format_time = '%H:%M:%S'

                    # Get start and end dates.
                    # date = datetime.datetime.now()
                    # actual_date = date.strftime(format_date)
                    # actual_time = date.strftime(format_time)

                    try:
                        # user_in_session : Info about user
                        # data_holder.user_locker : Info about locker
                        # PRINT, MATRICULA,FOLIO,FECHA FINAL,HORA FINAL,FECHAINICIO,TIPODERENTA,AREA,NOMBRELOCKER,TOTAL

                        # folio = "00001"
                        printer_status = self.printer_socket.connect_ex((self.host_vmc, 1026))
                        printer_text = "{},#{},{},{},{},{},{},{},{},{}".format(
                            command,
                            get_print_msg.user,
                            get_print_msg.numeration,
                            get_print_msg.end_date,
                            get_print_msg.end_time,
                            get_print_msg.start_date,
                            get_print_msg.rent_type,
                            self.data_holder.area_name,
                            get_print_msg.locker_id,
                            get_print_msg.total)
                        print printer_text
                        self.printer_socket.sendall(printer_text)
                        # self.printer_socket.sendall("PRINT, A000000,0003,23-02-2015,12:30,10:30,By_Time,CITA,A3,20")
                        print "PRINTER STATUS {}".format(printer_status)
                    except Exception as ex:
                        print "Error al comunicar con impresora {}".format(ex)

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

    @staticmethod
    def program_card(user=None, locker=None, end_date=datetime.datetime.today()):

        end_now = end_date.strftime('%Y-%m-%d %H:%M:%S')
        print "FINAL DATE {}".format(end_now)

        response = LockersSocket.LockerSocket().send_command(
            Commands.Commands.update_user(user, locker, end_now)
        )
        print 'UPDATE USER: {}'.format(response)
        # SEND COMMAND TO SALTO PROGRAMMER
        response = LockersSocket.LockerSocket().send_command(
            Commands.Commands.assign_new_key(user)
        )

        print 'Assign key: {}'.format(response)

        response = LockersSocket.LockerSocket().send_command(
            Commands.Commands.update_key(user)
        )
        print 'Update key: {}'.format(response)

    @staticmethod
    def program_two_cards(user=None, locker=None, locker2=None, end_date=datetime.datetime.today()):

        end_now = end_date.strftime('%Y-%m-%d %H:%M:%S')
        print "FINAL DATE {}".format(end_now)

        response = LockersSocket.LockerSocket().send_command(
            Commands.Commands.update_user_two(user, locker, locker2, end_now)
        )
        print 'UPDATE USER: {}'.format(response)
        # SEND COMMAND TO SALTO PROGRAMMER
        response = LockersSocket.LockerSocket().send_command(
            Commands.Commands.assign_new_key(user)
        )

        print 'Assign key: {}'.format(response)

        response = LockersSocket.LockerSocket().send_command(
            Commands.Commands.update_key(user)
        )
        print 'Update key: {}'.format(response)

    def get_rates(self):
        rates_msg = ApiMessages.Rates()
        rates = rates_msg.get_rates()

        for rate in rates:
            if rate.rate_unit == 'h':
                self.data_holder.rate_h = float(rate.rate_rate)
            elif rate.rate_unit == 'd':
                self.data_holder.rate_d = float(rate.rate_rate)
            elif rate.rate_unit == 'w':
                self.data_holder.rate_w = float(rate.rate_rate)
            elif rate.rate_unit == 's':
                self.data_holder.rate_s = float(rate.rate_rate)

        print "Tarifas por hora: h-{} d-{} semana-{} semestre-{}".format(self.data_holder.rate_h,
                                                                         self.data_holder.rate_d,
                                                                         self.data_holder.rate_w,
                                                                         self.data_holder.rate_s)

    def calculate_payment(self, p_start): # , balance=0.0):
        payment = 0

        try:
            # Obtener la zona horaria de la maquina y añadirla a la hora actual
            str_timezone_diff = datetime.datetime.now(pytz.timezone('America/Chihuahua')).strftime('%z')
            end_time = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S{}".format(str_timezone_diff))

            # hacer un parse de las horas para verificar que estén en el formato adecuado
            start = parse(p_start)
            end = parse(end_time)

            # calcular el pago por hora
            elapsed_time = end - start
            total_hours = math.ceil(elapsed_time.total_seconds() / 60 / 60)

            if total_hours < 24:
                rate = self.data_holder.rate_h
            elif total_hours < (24 * 7):
                rate = self.data_holder.rate_d
            else:
                rate = self.data_holder.rate_w

            payment = total_hours * rate # - balance
            self.data_holder.total_hours = total_hours

        except Exception as ex:
            print "ERROR AL CALCULAR PAGO - {}".format(ex)

        return payment

    def on_close(self, reason):
        # When stopping the socket, we must check to stop all services.
        print 'WebSocket closed\n{}'.format(reason)


"""
 Create a WebSocketServer, to listen to the front-end.
"""
WebSocketServer(
    ('127.0.0.1', 1024),  # Modify
    Resource({'/': EchoApplication})
).serve_forever()


"""
# Delete access
response = LockersSocket.LockerSocket().send_command(
Commands.Commands.delete_access_level(
self.data_holder.user_locker.locker_name
)
)
print 'Delete access: {}'.format(response)

response = LockersSocket.LockerSocket().send_command(
Commands.Commands.assign_access_level(
self.data_holder.user_locker.locker_name,
self.data_holder.card_key
)
)
print 'Assign access: {}'.format(response)

# PROGRAM CARD WHEN RENT IS TIME BASED
now_p = datetime.datetime.today()
now_plus_10 = datetime.datetime.today() + datetime.timedelta(minutes=10)
dow = now_p.weekday()
days=['0','0','0','0','0','0','0']
days[dow] = '1'
start_rent = "{}".format(now_p.strftime('%H:%M:%S'))
end_rent = "{}".format(now_plus_10.strftime('%H:%M:%S'))
print "{} - {}".format(start_rent, end_rent)
response = LockersSocket.LockerSocket().send_command(
Commands.Commands.assign_by_time(self.data_holder.user_locker.locker_id,
                             start_rent, end_rent, days)
)
print 'Set day of week & time: {}'.format(response)

# PROGRAM CARD WHEN RENT IS TIME BASED3

months = ['0','0','0','0','0','0','0','0','0','0','0','0']
curr_month = now_p.month
for int_month in range(1,13):
aux_str_month = "0"*31
arr_month = list(aux_str_month)
if int_month == curr_month:
arr_month[now_p.weekday()-1] = "1"
str_month = "".join(aux_str_month)
print str_month
months[int_month -1 ] = str_month

response = LockersSocket.LockerSocket().send_command(
Commands.Commands.assign_calendar(self.data_holder.user_locker.locker_id,
                             now_p.year,months)
)
print 'Set calendar: {}'.format(response)
"""