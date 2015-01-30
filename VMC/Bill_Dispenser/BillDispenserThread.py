__author__ = 'mgradob'

""" Imports """
import threading
from findertools import sleep

import serial

from VMC.Utils import Commands


class BillDispenserThread(threading.Thread):
    """
     Class BillDispenserThread
      Thread for COM connection with the bill dispenser.

      TODO: Define if the platform is Windows or Unix.
    """

    """ Global Variables """
    # COM variables
    com_port = None

    # Commands and VMCCommands object
    commands = Commands.BillCommands()

    # Balance
    balance = 0
    bill_count = 0
    bill_type = 0

    deposited_20, deposited_50, deposited_100, deposited_200, deposited_500 = False, False, False, False, False

    # Flags
    is_writing = False
    is_polling = False
    must_reset = False
    must_accept = False
    first_run = False

    # Thread communication
    socket_receive = []
    socket_response = ". ."

    def open_com(self):
        """ Creates and opens the serial port. """
        """
        coms = []

        print('Searching COMs...')
        for i in range(0, 255):
            try:
                av_port = serial.Serial(i)
                coms.append("COM" + str(i + 1))
                av_port.close()
            except serial.SerialException:
                pass

        print(coms)

        self.com_port_number = int(raw_input('Select COM port: ')) - 1
        """

        self.com_port = serial.Serial('/dev/tty.usbserial', 9600, parity=serial.PARITY_NONE)

        if self.com_port.isOpen():
            self.com_port.close()
        self.com_port.open()

        print('{} is open.'.format(self.com_port.name))

    def write_cmd(self, cmd=Commands.BillCommands(), in_waiting=1, sleep_thread=0.1):
        """
         Method for sending a command via serial port.
          Defaults: waits for 1 byte on the serial buffer, sleeps the thread for 100ms.
        """
        # Try to open the serial port. First check if it's open already.
        try:
            if self.com_port.isOpen():

                # Write the command (see Commands.py) to the serial port, and print it.
                self.com_port.write(cmd['cmd'])
                print('{} cmd sent'.format(cmd['name']))

                # Sleep the thread until we have the minimum required data or until we have a timeout (default=500ms).
                """
                timeout = 0
                while self.com_port.inWaiting() < in_waiting and timeout < 5:
                    timeout += 1
                    sleep(.1)
                if timeout >= 5:
                    raise serial.SerialException
                """

                # Read the required bytes from the serial port.
                reading = self.com_port.read(in_waiting)
                data = []
                for byte in reading:
                    data.append(ord(byte))

                print(data)

                # Flush the input and output buffers.
                self.com_port.flushInput()
                self.com_port.flushOutput()

                # Return the command received. Not all commands will use this.
                return data
        except serial.SerialException:
            # If a SerialException is catch then must restart the communication.
            self.must_reset = True
            print 'Error'
            return ''

    def write_status(self):
        """ Writes a Status command."""
        self.write_cmd(self.commands.BILL_STATUS, 4)

    def write_enable_all(self):
        """ Writes an Enable All command. """
        self.write_cmd(self.commands.BILL_ENABLE_ALL)

    def write_enable_escrow(self):
        """ Writes an Enable Escrow command. """
        self.write_cmd(self.commands.BILL_ENABLE_ESCROW)

    def write_disable_escrow(self):
        """ Writes an Enable Escrow command. """
        self.write_cmd(self.commands.BILL_DISABLE_ESCROW)

    def write_accept_escrow(self):
        """ Writes an Accept Escrow command. """
        self.write_cmd(self.commands.BILL_ACCEPT_ESCROW, 2)

    def write_reject_escrow(self):
        """ Writes a Reject Escrow command."""
        self.write_cmd(self.commands.BILL_REJECT_ESCROW)

    def init_sequence(self):
        """ Initialization sequence. """
        self.write_enable_all()
        self.write_status()
        pass

    def run(self):
        """ Run method for the thread. """

        # First run.
        # Must not reset and start the initialization sequence.
        read, reading = True, ''
        while read:
            self.must_reset = False
            self.init_sequence()
            while not self.must_reset:
                reading = 0
                if self.com_port.inWaiting() > 0:
                    reading = self.com_port.read()
                    reading = ord(reading)
                    #print reading

                if self.must_accept and self.bill_count == 0 and not self.first_run:
                    print "Initializing bill escrow..."
                    self.write_enable_escrow()
                    print "Deposit now"
                    self.first_run = True
                elif self.bill_count >= self.balance and self.first_run:
                    self.must_accept = False
                    self.balance = 0
                    self.bill_count = 0
                    self.first_run = False
                    self.socket_response = 'FINISHED {}'.format(self.bill_count - self.balance)
                elif self.must_accept:
                    if reading == 120:
                        print 'Validator Busy'
                    elif reading == 121:
                        print 'Validator Ready'
                    elif reading == 1:
                        self.bill_type = 1
                        if (self.balance - self.bill_count) >= 20:
                            self.com_port.write(self.commands.BILL_ACCEPT_ESCROW['cmd'])
                            self.deposited_20 = True
                        else:
                            self.com_port.write(self.commands.BILL_REJECT_ESCROW['cmd'])
                    elif reading == 2:
                        self.bill_type = 2
                        if (self.balance - self.bill_count) >= 50:
                            self.deposited_50 = True
                            self.com_port.write(self.commands.BILL_ACCEPT_ESCROW['cmd'])
                        else:
                            self.com_port.write(self.commands.BILL_REJECT_ESCROW['cmd'])
                    elif reading == 3:
                        self.bill_type = 3
                        if (self.balance - self.bill_count) >= 100:
                            self.deposited_100 = True
                            self.com_port.write(self.commands.BILL_ACCEPT_ESCROW['cmd'])
                        else:
                            self.com_port.write(self.commands.BILL_REJECT_ESCROW['cmd'])
                    elif reading == 4:
                        self.bill_type = 4
                        if (self.balance - self.bill_count) >= 200:
                            self.deposited_200 = True
                            self.com_port.write(self.commands.BILL_ACCEPT_ESCROW['cmd'])
                        else:
                            self.com_port.write(self.commands.BILL_REJECT_ESCROW['cmd'])
                    elif reading == 5:
                        self.bill_type = 5
                        if (self.balance - self.bill_count) >= 500:
                            self.deposited_500 = True
                            self.com_port.write(self.commands.BILL_ACCEPT_ESCROW['cmd'])
                        else:
                            self.com_port.write(self.commands.BILL_REJECT_ESCROW['cmd'])
                    elif reading == 172:
                        while self.com_port.inWaiting() < 1:
                            pass
                        print(ord(self.com_port.read(1)))

                        if self.bill_type == 1:
                            self.bill_count += 20
                            print 'Balance: ${}'.format(self.bill_count)
                            print 'Owes: ${}'.format(self.balance - self.bill_count)
                        elif self.bill_type == 2:
                            self.bill_count += 50
                            print 'Balance: ${}'.format(self.bill_count)
                            print 'Owes: ${}'.format(self.balance - self.bill_count)
                        elif self.bill_type == 3:
                            self.bill_count += 100
                            print 'Balance: ${}'.format(self.bill_count)
                            print 'Owes: ${}'.format(self.balance - self.bill_count)
                        elif self.bill_type == 4:
                            self.bill_count += 200
                            print 'Balance: ${}'.format(self.bill_count)
                            print 'Owes: ${}'.format(self.balance - self.bill_count)
                        elif self.bill_type == 5:
                            self.bill_count += 500
                            print 'Balance: ${}'.format(self.bill_count)
                            print 'Owes: ${}'.format(self.balance - self.bill_count)

    def write_accept(self):


        while (not self.deposited_20) and (not self.deposited_50) \
                and (not self.deposited_100) and (not self.deposited_200)\
                and (not self.deposited_500):
            pass

        self.must_accept = False
        if self.deposited_20:
            self.deposited_20 = False
            return 20

        elif self.deposited_50:
            self.deposited_50 = False
            return 50

        elif self.deposited_100:
            self.deposited_100 = False
            return 100

        elif self.deposited_200:
            self.deposited_200 = False
            return 200

        elif self.deposited_500:
            self.deposited_500 = False
            return 500

        else:
            return 0

    def set_balance(self, balance):
        self.balance = balance



    def socket_com(self, command=''):
        cmd, param1 = command.split()

        if cmd == 'ACCEPT':
            self.must_accept = True
            return self.write_accept()

        else:
            pass

    def __init__(self):
        """ Thread initialization """
        super(BillDispenserThread, self).__init__()
        self.open_com()