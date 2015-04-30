__author__ = 'ardzoht'

import socket
import threading
import sys
import PrinterThread


class PrinterController(threading.Thread):
    """
    Class PrinterController
    Implements threading to run a SocketServer
    """
    client_address = ""
    port = 0
    connects = 0
    data = None
    printer_thread = None


    def __init__(self, address, port, connections):
        super(PrinterController, self).__init__()

        # Init variables for the socket connection
        self.addr = address
        self.port = port
        self.connects = connections

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Socket init...')

        try:
            self.socket.bind((self.addr, self.port))
        except socket.error as msg:
            print('Failed bind. Error code: {}'.format(msg))
            sys.exit()
        print('PRINTER bind on address %s') % self.addr

        self.socket.listen(self.connects)
        print('Socket listening, conns: {}'.format(self.connects))

        self.printer_thread = PrinterThread.PrinterThread()
        self.printer_thread.start()

    def run(self):
        while True:
            connection, client_address = self.socket.accept()

            try:
                print 'Connection from {}'.format(client_address)
                while True:
                    self.data = connection.recv(1024)

                    if self.data:
                        print 'Received {}'.format(self.data)
                        inst = self.data.split('#')
                        print inst[1]
                        if inst[0] == 'PRINT,':
                            user_id, folio, date, time, start_time, \
                            scheme,locker, area, total =  inst[1].split(',')
                             # Set the parameters
                            self.printer_thread.set_ticker_parameters(user_id, folio, date, area, time, start_time,
                                                                    locker, scheme, total)
                            self.printer_thread.printer_ready = True

                        connection.sendall('OK {}'.format(self.data))


                    else:
                        print 'No more data from {}'.format(self.client_address)
                        break
            except Exception as ex:
                print "Error de PRINTER"
                print ex

            connection.close()
