__author__ = 'mgradob'

from geventwebsocket import WebSocketServer, WebSocketApplication, Resource

from Lockers import LockersThread
from VMC import VMC


class EchoApplication(WebSocketApplication):
    """
    EchoApplication Class.
     A socket listening forever to the front-end, which will manage the vending services and the lockers.
    """
    vmc = VMC
    locker = None

    def on_open(self):
        """
        Initialization of the system (VMC, Websocket)
        """
        print 'Connection opened'

        # Run a new thread of the VMC module.
        #self.vmc = VMC.VMC('127.0.0.1', 49153, 1)
        #self.vmc.run()

    def on_message(self, message):
        """
        When we receive a message from the front-end, call for the different services required.
        """
        print 'Received message: {}'.format(message)

        response = ''

        if message == 'LOG_IN':
            locker_thread = LockersThread.LockerThread(LockersThread.Commands.read_key())

            response = 'OK'
        if message == 'OPEN_LOCKER':
            locker_thread = LockersThread.LockerThread(LockersThread.Commands.open_locker())
            response = 'OPEN'

        self.ws.send(response)

        print 'Answered: {}'.format(response)

    def on_close(self, reason):
        """
        When stopping the socket,we must check to stop all services.
        """
        print 'WebSocket closed\n{}'.format(reason)

""" Create a WebSocketServer, to listen to the front-end. """
WebSocketServer(
    ('localhost', 49152),
    Resource({'/': EchoApplication})
).serve_forever()