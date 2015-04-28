# coding=utf-8
__author__ = 'mgradob'

""" Imports """
from VMC.Coin_Changer import Changer_Thread
from VMC.Bill_Dispenser import BillDispenserThread
import socket
import threading
from time import sleep


class VmcController(threading.Thread):
    """
     Class ServerSocketTest
      Initializes a server socket on localhost:49135.
    """

    """ Global Variables """
    addr = ""
    port = 0
    conns = 0
    socket = None
    changer_thread = None
    bill_dispenser_thread = None
    poll_thread = None
    command = ""

    # Initialization
    def __init__(self, address='127.0.0.1', port=1025, connections=1):
        """ __init__ for the main program. """
        super(VmcController, self).__init__()
        self.addr = address
        self.port = port
        self.conns = connections
        self.start_socket_server()

    def run(self):
        while 1:
            conn, addr = self.socket.accept()
            print 'Client connected'

            while True:
                try:
                    # Wait for data (1024)
                    self.command = conn.recv(1024)
                    print('Command received: {}'.format(self.command))

                    # If data received is null close the connection.
                    # Else, split the command: data[0] = DISPENSE, data[1] = NN.CC
                    if not self.command:
                        break
                    else:
                        data = self.command.split()

                        # Validate for the DISPENSE command. Else send an error message to the socket.
                        # Split NN.CC as: units:NN, cents:CC
                        if data[0] == 'DISPENSE':
                            thread_response = self.changer_thread.socket_com(self.command)

                            # Reset the response, acknowledge the command.
                            conn.sendall('Thread_response: {}'.format(thread_response))

                        elif data[0] == 'ACCEPT':
                            balance, deposit, deposit_bill = float(data[1]), float(0), float(0)
                            self.bill_dispenser_thread.balance = balance
                            while deposit+deposit_bill < balance:

                                if deposit+deposit_bill >= balance:
                                    break

                                else:
                                    try:

                                        #deposit += self.changer_thread.socket_com('ACCEPT {}'.format(balance))
                                         deposit_bill += self.bill_dispenser_thread.socket_com('ACCEPTBILL {}'.format(balance))
                                    except Exception as ex:
                                        print ex
                                    print 'VMC: Deposit: {}, Balance: {}'.format(deposit+deposit_bill, balance)
                                    conn.sendall('DEPOSIT: {}'.format(deposit+deposit_bill))

                            sleep(0.5)

                            if deposit+deposit_bill > balance:
                                dif = float(deposit+deposit_bill-balance)
                                print 'Dif: {}'.format(dif)
                                # TODO Lógica del dispense
                                conn.sendall('DIFFERENCE {}'.format(dif))
                                try:
                                    self.changer_thread.socket_com('DISPENSE {}'.format(dif))
                                except Exception as ex:
                                    print "{}".format(ex)
                                    conn.sendall('DIFFERENCE {}'.format(dif))
                            print 'Balance completed'
                            conn.sendall('COMPLETE')

                        elif data[0] == 'CANCEL':
                            self.bill_dispenser_thread.write_reject_escrow()
                        else:
                            print('Incorrect cmd')
                            conn.sendall('ERROR')

                except Exception as ex:
                    print "ERROR EN EL VMC - {}".format(ex)

            # Close the connection on an error
            conn.close()

    def start_socket_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Socket created')
        try:
            self.socket.bind((self.addr, self.port))
        except socket.error as msg:
            print('Bind failed. Error code: {}'.format(msg))
            quit()
        print('Socket bind complete')
        self.socket.listen(self.conns)
        print('Socket listening, conns: {}'.format(self.conns))
        self.changer_thread = Changer_Thread.Changer()
        self.changer_thread.start()
        self.bill_dispenser_thread = BillDispenserThread.BillDispenserThread()
        self.bill_dispenser_thread.start()
