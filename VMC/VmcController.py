# coding=utf-8
__author__ = 'mgradob'

""" Imports """
from VMC.Coin_Changer import Changer_Thread
from VMC.Bill_Dispenser import BillValidator_Thread
from VMC.Utils import Commands
import socket
import threading
from time import sleep
import datetime
import serial


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
    commands = Commands.BillCommands()

    # Initialization
    def __init__(self, address='127.0.0.1', port=1025, connections=1):
        """ __init__ for the main program. """
        super(VmcController, self).__init__()
        self.addr = address
        self.port = port
        self.conns = connections
        self.start_socket_server()

    def run(self):
        """
        Running thread controller that calculates both the accepting and dispensing actions
        of the Changer and the Bill validator


        :return:
        Sends the commands to the Main Controller for further control to the Frontend
        """
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
                            print "Ready to accept"
                            # Enables the Bill Validator for accepting bills
                            self.bill_dispenser_thread.write_thread.write_enable_all()
                            #self.changer_thread.write_thread.write_cmd(self.changer_thread.commands.enable_tubes())

                            # Init variables of balance, and deposit values
                            balance, deposit, deposit_bill = float(data[1]), float(0), float(0)
                            sum = 0
                            # Change timeout

                            # Timeout initialization
                            default_timeout = 15
                            timeout_counter = default_timeout
                            timeout = True
                            timeout_date = datetime.datetime.today() + datetime.timedelta(seconds=10)

                            while sum < balance:

                                if sum >= balance:
                                    break

                                else:
                                    try:
                                        # Accepts bills and coins until the sum is equal or greater than the debt
                                        #deposit = self.changer_thread.\
                                        #    socket_com('ACCEPT {}'.format(balance))
                                        deposit_bill = self.bill_dispenser_thread.\
                                            socket_com('ACCEPTBILL {}'.format(balance))
                                    except Exception as ex:
                                        print ex

                                    # If a bill or coin is deposit, it adds the value to the sum, and resets the counter
                                    if deposit != 0 or deposit_bill != 0:
                                        print "Deposited"
                                        timeout_counter = default_timeout
                                        timeout_date = datetime.datetime.today() + datetime.timedelta(seconds=10)
                                        sum += deposit_bill + deposit
                                        print 'VMC: Deposit: {}, Balance: {}'.format(sum, balance)
                                        conn.sendall('DEPOSIT {}'.format(sum))

                                timeout_counter -= 1
                                if datetime.datetime.today() > timeout_date:
                                    #In case of a timeout
                                    timeout = False
                                    print "TIMEOUT POR TIEMPO"
                                    break

                                # if timeout_counter <= 0:
                                #    timeout = False
                                #   break

                            sleep(0.5)

                            if not timeout:
                                #self.changer_thread.write_thread.write_cmd(self.changer_thread.commands.disable_tubes())
                                self.bill_dispenser_thread.write_thread.write_disable_all()
                                conn.sendall('TIMEOUT {}'.format(sum))
                            else:
                                # Calculates the difference for dispense action
                                dif = float(sum-balance)
                                print 'Dif: {}'.format(dif)
                                self.bill_dispenser_thread.write_thread.write_disable_all()
                                #self.changer_thread.write_thread.write_cmd(self.changer_thread.commands.disable_tubes())
                                #self.changer_thread.socket_com('DISPENSE {}'.format(dif))
                                #If there is a coin that couldn't be dispensed, it deposits the value to user account

                         #       if self.changer_thread.read_thread.dispense_error:
                         #           print "Error on dispense"
                         #           self.changer_thread.read_thread.dispense_error = False
                                    #Sends the amount difference
                         #           if self.changer_thread.error_amount > 0:
                         #               print "Amount"
                         #               conn.sendall('DIFFERENCE {}'.format(self.changer_thread.error_amount))
                                    #Sends the entire difference, in case that none coin couldn't be dispensed
                         #           else:
                         #               print "Difference"
                         #               conn.sendall('DIFFERENCE {}'.format(dif))

                                print 'Balance completed'
                                conn.sendall('COMPLETE')
                        # In case of a cancel action, it disables all the payments methods
                        elif data[0] == 'CANCEL':
                            self.bill_dispenser_thread.write_thread.write_disable_all()
                        #    self.changer_thread.write_thread.write_cmd(self.changer_thread.commands.disable_tubes())
                        else:
                            print('Incorrect cmd')
                            conn.sendall('ERROR')

                except Exception as ex:
                    print "ERROR EN EL VMC - {}".format(ex)

            # Close the connection on an error
            conn.close()

    def start_serial(self):
        try:
            global serial_port

            #Lo cambie para poder conectar la impresora en el COM6
            serial_port = serial.Serial('/dev/cu.usbserial-FTVSGL58', 115200, timeout=1, parity=serial.PARITY_NONE)
            print 'Serial port open'
        except serial.SerialException:
            print 'Port not created'

        if serial_port.isOpen():
            serial_port.close()

        serial_port.open()

    def start_socket_server(self):
        """
        Starts the socket and the threads of Bill, Coin_Changer
        :return:
        """
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
        self.start_serial()
        #self.changer_thread = Changer_Thread.Changer(serial_port)
        #self.changer_thread.start()
        self.bill_dispenser_thread = BillValidator_Thread.BillValidator(serial_port)
        self.bill_dispenser_thread.start()
