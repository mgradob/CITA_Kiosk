__author__ = 'mgradob'

""" Imports """
import socket
import threading


class LockerThread(threading.Thread):
    """
    LockerThread Class.
     Thread to manage communication with Salto Lockers.
    """

    """ Global Variables """
    sock = None
    cmd = None
    host, port = '10.33.10.194', 8050

    def run(self):
        """ Run the process. """

        # Get the lockers socket information.
        for info in socket.getaddrinfo(self.host, self.port, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = info

            try:
                self.sock = socket.socket(af, socktype, proto)
            except socket.error:
                self.sock = None
                continue

            try:
                self.sock.connect((self.host, self.port))
            except socket.error:
                self.sock.close()
                self.sock = None
                continue

        try:
            self.sock.sendall(self.cmd)
            self.sock.sendall(self.cmd)
            print('Sent: {}'.format(self.cmd))

            received = self.sock.recv(1024)
        finally:
            self.sock.close()

        print('Received: {}'.format(received))

    def __init__(self, Command):
        """ Initialize module """
        super(LockerThread, self).__init__()
        self.cmd = Command
        self.run()