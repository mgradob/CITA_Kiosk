from VMC.Coin_Changer import ChangerThread

__author__ = 'mgradob'

""" Imports """
import socket
import sys
import threading


class VMC(threading.Thread):
    """
     Class ServerSocketTest
      Initializes a server socket on localhost:9999.

      A dispense command is defined as: DISPENSE NN.CC, where NN = units, CC = cents.

      TODO: Update documentation.
      TODO: Implement various commands.
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
    def __init__(self, address, port, connections):
        """ __init__ for the main program. """
        super(VMC, self).__init__()

        # Initialization of global variables.
        self.addr = address
        self.port = port
        self.conns = connections

        # Create the socket object.
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Socket created')

        # Try to bind the socket to the address and port. On error, exit the program.
        try:
            self.socket.bind((self.addr, self.port))
        except socket.error as msg:
            print('Bind failed. Error code: {}'.format(msg))
            sys.exit()
        print('Socket bind complete')

        # Define the number of connections to listen to (1).
        self.socket.listen(self.conns)
        print('Socket listening, conns: {}'.format(self.conns))

        # Create and start a ChangerThread thread.
        self.changer_thread = ChangerThread.ChangerThread()
        self.changer_thread.start()

        # Create and start a BillDispenserThread
        #self.bill_dispenser_thread = BillDispenserThread.BillDispenserThread()
        #self.bill_dispenser_thread.start()

        # Infinite loop. Open and close the socket.
        while 1:
            conn, addr = self.socket.accept()

            while 1:
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
                        units, cents = data[1].split('.')

                        # Tell the COMThread to dispense the given credit.
                        self.changer_thread.socket_receive = [int(units), int(cents)]
                        self.changer_thread.must_dispense = True

                        # Wait for a response and print it.
                        while self.changer_thread.socket_response == '':
                            pass
                        print(self.changer_thread.socket_response)

                        # Reset the response, acknowledge the command.
                        self.changer_thread.socket_response = ''
                        conn.sendall('{} OK'.format(self.command))

                    elif data[0] == 'ACCEPT':
                        """
                        units, cents = data[1].split('.')
                        self.bill_dispenser_thread.socket_receive = [units, cents]
                        self.bill_dispenser_thread.must_accept = True

                        while not self.bill_dispenser_thread.socket_response.split()[0] == 'FINISHED':
                            pass

                        self.bill_dispenser_thread.socket_response = '. .'
                        conn.sendall('{} OK'.format(self.command))
                        """
                    else:
                        print('Incorrect cmd')
                        conn.sendall('Error')

            # Close the connection on an error
            conn.close()