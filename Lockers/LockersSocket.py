__author__ = 'mgradob'

""" Imports """
import socket
from Lockers.Utils import Commands
from Lockers.Utils import XmlParser


class LockerSocket():
    """
    LockerThread Class.
     Thread to manage communication with Salto Lockers.
    """

    """ Global Variables """
    sock = None
    cmd = None
    host, port = '10.33.2.249', 8050
    parser = XmlParser.XmlParser()
    received, response = '', ''

    def send_command(self, command):
        """ Run the process. """
        self.cmd = command

        # Get the lockers socket information.
        for info in socket.getaddrinfo(self.host, self.port, socket.AF_UNSPEC, socket.SOCK_STREAM):
            # Open connection to the Salto Socket.
            af, socktype, proto, canonname, sa = info

            try:
                self.sock = socket.socket(af, socktype, proto)
            except:
                self.sock = None
                continue

            try:
                self.sock.connect((self.host, self.port))
            except:
                self.sock.close()
                self.sock = None
                continue

        try:
            self.sock.sendall(self.cmd)
            self.sock.sendall(self.cmd)
            print('Sent: {}'.format(self.cmd))

            self.received = self.sock.recv(1024)

        finally:
            if self.sock is not None:
                self.sock.close()

                # Check for answer, to know which info to respond.
                if self.cmd == Commands.Commands.read_key():
                    self.response = self.parser.get_rom_code(self.received)
                else:
                    self.response = self.received

                # Return the data.
                return self.response
            else:
                return 'Communication error with Salto'

    def __init__(self):
        """ Initialize module """
        pass