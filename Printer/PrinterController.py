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
    client_address = "127.0.0.1"
    port = 1026
    connects = 0
    data = None


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
        print('Successful bind on address %s') % self.addr

        self.socket.listen(self.connects)
        print('Socket listening, conns: {}'.format(self.connects))

        while True:
            connection, client_address = self.socket.accept()

            try:
                print 'Connection from {}'.format(client_address)
                while True:
                    self.data = connection.recv(1024)

                    if self.data:
                        print 'Received {}'.format(self.data)
                        cmd, data = self.data.split()
                        print cmd
                        if cmd == 'PRINT,':
                            user_id, folio, date, time, start_time, scheme, locker, area = data.split(',')
                            print [['USER ID: ', user_id], ['FOLIO: ', folio],
                                   ['DATE: ', date], ['TIME: ', time],
                                   ['START: ', start_time],['RENT: ', scheme],
                                   ['LOCKER: ', locker], ['AREA: ', area]]

                            #Starts a thread to communicate with the printer
                            printer_thread = PrinterThread.PrinterThread()
                            printer_thread.settickerparameters(user_id, folio, date, area, time, start_time,
                            locker, scheme)
                            printer_thread.printer_ready = True
                            printer_thread.print_ticket()


                        connection.sendall('OK {}'.format(self.data))


                    else:
                        print 'No more data from {}'.format(self.addr)
                        break
            finally:
                connection.close()

ticket_thread = PrinterController('127.0.0.1', 1026, 1)
ticket_thread.run()