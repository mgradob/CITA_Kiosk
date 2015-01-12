__author__ = 'mgradob'

from geventwebsocket import WebSocketServer, Resource, WebSocketApplication
from Utils import JsonMessages, ApiMessages, DataHolder
from Lockers import LockersSocket
from Lockers.Utils import Commands
import datetime, time
import socket
from VMC import VmcController


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

    # Open socket to the VMC Controller
    vmc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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

                    if (self.data_holder.card_key == "403"): #No hay tarjeta
                        print "No hay tarjeta"
                        self.response = JsonMessages.Error(True, "Tarjeta", "No hay tarjeta").get_json()
                    else:
                        try:
                            # Check for key existance in DB.
                            self.user_in_session = ApiMessages.User(self.data_holder.card_key).get_user()
                            registred = ApiMessages.Lockers().has_assigned_locker(self.data_holder.card_key)

                            # Create Json response for the user.
                            user = '{} {} {}'.format(
                                self.user_in_session.user_name,
                                self.user_in_session.user_ap,
                                self.user_in_session.user_am
                            )

                            self.response = JsonMessages.User(
                                registred, '',
                                user,
                                self.user_in_session.user_mat,
                                1,
                                '',
                                '',
                                0
                            ).get_json()
                        except Exception:
                            print "Error al obtener Usuario"
                            self.response = JsonMessages.Error(True, "Usuario", "No se ha encontrado el usuario").get_json()

                elif command == 'SOLICIT':
                    # Create a Solicit message class, to easily handle message data.
                    # Create a Lockers message class.
                    solicit_msg = JsonMessages.Solicit(message)
                    api_msg = ApiMessages.Lockers()

                    # Get the first available locker.
                    self.locker = api_msg.get_available_lockers()[0]
                    self.data_holder.user_locker = self.locker

                    # Get the area_id of the selected locker.
                    for area in api_msg.areas_list:
                        if area.area_name == solicit_msg.area:
                            self.locker_area_id = area.area_id
                        else:
                            self.locker_area_id = '0'

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
                        total = int(minutes_to_pay * 0.00002)#Dumy rate
                        self.data_holder.total = total #8.5

                        # Assign the locker with the calculated pay.
                        api_msg.assign_locker(
                            self.data_holder.card_key,
                            self.data_holder.user_locker,
                            self.locker_area_id, start_date
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
                            self.locker_area_id, start_date
                        )

                        # Create Json response for confirmation.
                        self.response = JsonMessages.Confirm(
                            inicio=start_date,
                            locker=self.data_holder.user_locker.locker_name,
                            total='TIME'
                        ).get_json()
                        self.ws.send(self.response)

                    # ---TODO Implement payment calculation.
                    # --------------------------------------

                elif command == 'OK':
                    try:
                        sock_status = self.vmc_socket.connect_ex((self.host_vmc, self. port_vmc))
                        self.vmc_socket.sendall('ACCEPT {}'.format( self.data_holder.total)) #Total a pagar en el monedero
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

                        self.ws.send(JsonMessages.Paid().get_json())

                    except Exception as ex:
                        print ex
                        print "Error al comunicar con el monedero"

                elif command == 'ACCEPT':## POR TIEMPO
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

                    self.ws.send(JsonMessages.Paid().get_json())

                    # pass
                    # Configure user
                    # Configure user id with access times

                    #self.ws.send(JsonMessages.Accept().get_json())

                elif command == 'CANCEL':
                    # TODO Implement logic for cancel an operation.
                    print 'Canceling'

                elif command == 'PRINT':
                    # TODO Implement logic for printer.
                    print 'Printing ticket'

                elif command == 'LOG_OUT':
                    # TODO Implement logic for closing session.
                    print 'Login Out'

                else:
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

    def on_close(self, reason):
        """
        When stopping the socket, we must check to stop all services.
        """
        print 'WebSocket closed\n{}'.format(reason)

"""
 Create a WebSocketServer, to listen to the front-end.
"""
WebSocketServer(
    ('127.0.0.1', 1024), # Modify
    Resource({'/': EchoApplication})
).serve_forever()