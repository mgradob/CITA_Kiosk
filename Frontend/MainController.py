__author__ = 'mgradob'

from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from Utils import JsonMessages, ApiMessages, DataHolder
from Lockers import LockersSocket
from Lockers.Utils import Commands
import datetime
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
    host, port = '127.0.0.1', 49154

    # Run a new thread of the VMC module.
    vmc = VmcController.VmcController('localhost', 49154, 1)
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

                    # Check for key existance in DB.
                    self.user_in_session = ApiMessages.User(self.data_holder.card_key).get_user()
                    registred = ApiMessages.Lockers().has_assigned_locker(self.data_holder.card_key)

                    # Create Json response for the user.
                    # TODO Validate with real locker and user data.
                    user = '{} {} {}'.format(self.user_in_session.user_name, self.user_in_session.user_ap, self.user_in_session.user_am)
                    self.response = JsonMessages.User(registred, '', user, self.user_in_session.user_mat, 1, '', '', 0).get_json()

                elif command == 'SOLICIT':
                    # Create a Solicit message class.
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

                    # Get start and end dates.
                    date = datetime.datetime.now()
                    start_date = '{}-{}-{} {}:{}:{}'.format(date.year, date.month, date.day, date.hour, date.minute, date.second)
                    end_date = str(datetime.datetime(2014, 12, 4, 23, 59, 59))

                    # --- TODO Implement locker assignation.
                    api_msg.assign_locker(self.data_holder.card_key, self.data_holder.user_locker, self.locker_area_id, start_date)

                    # Create Json response for confirmation.
                    self.response = JsonMessages.Confirm(start_date, end_date, self.data_holder.user_locker.locker_name, 8.5).get_json()
                    self.ws.send(self.response)

                    # ---TODO Implement payment calculation.
                    # --------------------------------------

                elif command == 'OK':
                    self.vmc_socket.connect((self.host, self. port))
                    self.vmc_socket.sendall('ACCEPT {}'.format(8.5))

                    while True:
                        self.socket_data_in = self.vmc_socket.recv(1024)

                        if self.socket_data_in == 'COMPLETE':
                            break
                        else:
                            balance = self.socket_data_in.split()[1]
                            print balance
                            self.response = JsonMessages.Deposit(balance).get_json()
                            self.ws.send(self.response)

                    response = LockersSocket.LockerSocket().send_command(Commands.Commands.assign_access_level(self.data_holder.user_locker.locker_name, self.data_holder.card_key))
                    print 'Assign access: {}'.format(response)

                    response = LockersSocket.LockerSocket().send_command(Commands.Commands.assign_new_key(self.data_holder.card_key))
                    print 'Assign key: {}'.format(response)

                    self.ws.send(JsonMessages.Paid().get_json())

                elif command == 'CANCEL':
                    # TODO Implement logic for cancel an operation.
                    print 'Canceling'

                elif command == 'PRINT':
                    # TODO Implement logic for printer.
                    print 'Printing ticket'

                elif command == 'LOG_OUT':
                    # TODO Implement logic for clossing session.
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

    def on_close(self, reason):
        """
        When stopping the socket, we must check to stop all services.
        """
        print 'WebSocket closed\n{}'.format(reason)

"""
 Create a WebSocketServer, to listen to the front-end.
"""
WebSocketServer(
    ('10.33.18.104', 49153),
    Resource({'/': EchoApplication})
).serve_forever()
