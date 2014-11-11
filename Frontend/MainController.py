__author__ = 'mgradob'

from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from Utils import JsonMessages, ApiMessages, Models
from Lockers import LockersSocket
from Lockers.Utils import Commands
#from VMC import VmcController


class EchoApplication(WebSocketApplication):
    """
    EchoApplication Class.
     A socket listening forever to the front-end, which will manage the vending services and the lockers.
    """
    #vmc = VmcController
    locker = None
    user_in_session = None
    resend = False
    response, response_ant = '', ''

    def on_open(self):
        """
        Initialization of the system (VMC, Websocket)
        """
        print 'Connection opened'

        # Run a new thread of the VMC module.
        # self.vmc = VmcController.VmcController('localhost', 49154, 1)
        # self.vmc.start()

    def on_message(self, message):
        """
        When we receive a message from the front-end, call for the different services required.
        """
        if message is None:
            print 'Null message received'
        else:
            try:
                command = JsonMessages.Deserializer().get_command(message)
                print 'Received message: {}'.format(command)

                if command == 'READY':
                    self.resend = True

                elif command == 'LOG_IN':
                    locker_socket = LockersSocket.LockerSocket()
                    card_key = locker_socket.send_command(Commands.Commands.read_key())[:8]
                    print card_key

                    # TODO check for key existance in DB
                    # self.user_in_session = ApiMessages.User(card_key).get_user()

                    #
                    # if card_key == 'Communication error with Salto':
                    #     response = card_key
                    # else:
                    #     response = 'INIT_SESSION'
                    self.response = 'OK'
                    self.response_ant = self.response
                else:
                    self.response = 'Message not supported'

                if self.resend:
                    self.ws.send(self.response_ant)
                else:
                    self.ws.send(self.response)

                print 'Answered: {}'.format(self.response)

            except Exception:
                print 'Something happened'

    def on_close(self, reason):
        """
        When stopping the socket, we must check to stop all services.
        """
        print 'WebSocket closed\n{}'.format(reason)


"""
 Create a WebSocketServer, to listen to the front-end.
"""
WebSocketServer(
    ('localhost', 49153),
    Resource({'/': EchoApplication})
).serve_forever()