import time

__author__ = 'mgradob'

""" Imports """
import threading
import serial

from VMC.Utils import Commands


class BillDispenserThread(threading.Thread):
    """
     Class BillDispenserThread
      Thread for COM connection with the bill dispenser.

      TODO: Define if the platform is Windows or Unix.
    """

    """ Global Variables """

    # Commands and VMCCommands object
    commands = Commands.BillCommands()

    # Balance
    balance = 0
    bill_count = 0
    bill_type = 0

    deposited_20, deposited_50, deposited_100, deposited_200 = False, False, False, False

    # Flags
    is_writing = False
    is_polling = False
    must_reset = False
    must_accept = False
    first_run = False

    # Thread communication
    socket_receive = []
    socket_response = ". ."

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
            time.sleep(sleep_thread)
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

    def write_disable_all(self):
        "Writes a Disable All command"
        self.write_cmd(self.commands.BILL_DISABLE_ALL)

    def init_sequence(self):
        """ Initialization sequence. """
        self.write_disable_all()
        self.write_status()
        pass

    def run(self):
        """ Run method for the thread. """
        # First run.
        # Must not reset and start the initialization sequence.
        read, reading = True, ''
        while read:
            try:

                self.must_reset = False
                self.init_sequence()

                while not self.must_reset:
                    reading = 0
                    com_port = self.com_port
                    if com_port.inWaiting() > 0:
                        reading = com_port.read()
                        try:
                            reading = ord(reading)
                            print reading
                        except Exception as ex:
                            pass

                    if self.must_accept:
                        if reading == 120:
                            print 'Validator Busy'
                        elif reading == 121:
                            print 'Validator Ready'
                        elif reading == 1:
                            self.bill_type = 1
                            self.deposited_20 = True
                        elif reading == 2:
                            self.bill_type = 2
                            self.deposited_50 = True
                        elif reading == 3:
                            self.bill_type = 3
                            self.deposited_100 = True
                        elif reading == 4:
                            self.bill_type = 4
                            self.deposited_200 = True
                        elif reading == 5:
                                com_port.write(self.commands.BILL_REJECT_ESCROW['cmd'])
                        elif reading == 172:
                            while com_port.inWaiting() < 1:
                                pass
                            print(ord(com_port.read(1)))

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
            except serial.SerialException:
                print 'Serial error'

    def write_accept(self):
        if(not self.deposited_20) and (not self.deposited_50) \
                and (not self.deposited_100) and (not self.deposited_200):
            pass
            time.sleep(.5)
            return 0
        else:

            if self.deposited_20:
                self.deposited_20 = False
                return 20.0

            elif self.deposited_50:
                self.deposited_50 = False
                return 50.0

            elif self.deposited_100:
                self.deposited_100 = False
                return 100.0

            elif self.deposited_200:
                self.deposited_200 = False
                return 200.0

            else:
                return 0

    def socket_com(self, command=''):
        cmd, param1 = command.split()

        if cmd == 'ACCEPTBILL':
            self.must_accept = True
            return self.write_accept()

        else:
            self.must_accept = False

    def __init__(self, changer_port):
        """ Thread initialization """
        self.com_port = changer_port
        super(BillDispenserThread, self).__init__(changer_port)
        # self.open_com() // Not used with protocol v3