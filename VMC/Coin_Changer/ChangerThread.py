__author__ = 'Miguel'

""" Imports """
import threading
from time import sleep

import serial

from VMC.Utils import Commands


class ChangerThread(threading.Thread):
    """
     Class ChangerThread.
      Thread for COM connection and data handling with the changer.

      TODO: Define if the platform is Windows or Unix.
    """

    """ Global Variables """
    # COM variables
    com_port_number = 0
    com_port = None

    # Commands and VMCCommands object
    commands = Commands.VmcCommands()

    # Flags
    is_writing = False
    is_polling = False
    must_dispense = False
    must_reset = False

    # Thread Communication
    socket_receive = []
    socket_response = ""

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

        self.com_port = serial.Serial('/dev/tty.usbserial', 115200, timeout=1, parity=serial.PARITY_NONE, rtscts=1)

        if self.com_port.isOpen():
            self.com_port.close()
        self.com_port.open()

        print('{} is open.'.format(self.com_port.name))

    def write_cmd(self, cmd=Commands.VmcCommands(), in_waiting=0, sleep_thread=0.25):
        """
         Method for sending a command via serial port.
          Defaults: waits for 0 byte on the serial buffer, sleeps the thread for 100ms.
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
                while self.com_port.inWaiting() < in_waiting and timeout < 10:
                    timeout += 1
                    sleep(.5)
                if timeout >= 10:
                    raise serial.SerialException
                """

                # Read the required bytes from the serial port.
                data = ''

                if in_waiting > 0:
                    while not data[-2:] == 'X9':
                        data += self.com_port.read()
                    # Evaluate the data received.
                    # If the last two bytes are 'X9' then we have a correct package.
                    if data[-2:] == 'X9':
                        print('Correct byte received: {}'.format(data))
                    else:
                        print('Wrong byte: {}'.format(data))

                    sleep(sleep_thread)
                else:
                    print(self.com_port.readline())

                self.com_port.flushInput()
                self.com_port.flushOutput()

        except serial.SerialException:
            # If a SerialException is catch then must restart the communication.
            self.must_reset = True
            sleep(sleep_thread)

    def write_poll(self):
        """ Writes a Poll command. """
        self.write_cmd(self.commands.POLL, 6)

    def write_reset(self):
        """ Writes a Reset command. """
        self.write_cmd(self.commands.RESET, 4, 1)
        sleep(.5)

    def write_setup(self):
        """ Writes a Setup command. """
        self.write_cmd(self.commands.SETUP, 1)
        self.write_cmd(self.commands.ACK)

    def write_tube_status(self):
        """ Writes a Status command. """
        self.write_cmd(self.commands.TUBE_STATUS, 1)
        self.write_cmd(self.commands.ACK)

    def write_coin_type(self):
        """ Writes a Coin Type command. """
        self.write_cmd(self.commands.COIN_TYPE, 1)

    def write_dispense(self, units=0, cents=0):
        """ Writes a Dispense command. Also evaluates which coins should be dispensed. """
        # Evaluate coins.
        res = units
        quantity_10 = res / 10
        res %= 10
        quantity_5 = res / 5
        res %= 5
        quantity_2 = res / 2
        res %= 2
        quantity_1 = res / 1

        quantity_50c = cents / 5

        # Dispense coins depending on the coins it should dispense.
        if not quantity_10 == 0:
            self.write_cmd(self.commands.dispense_10(quantity_10), 2)
        if not quantity_5 == 0:
            self.write_cmd(self.commands.dispense(quantity_5, 4), 0)
        if not quantity_2 == 0:
            self.write_cmd(self.commands.dispense(quantity_2, 3), 0)
        if not quantity_1 == 0:
            self.write_cmd(self.commands.dispense(quantity_1, 2), 0)
        if not quantity_50c == 0:
            self.write_cmd(self.commands.dispense(quantity_50c, 0), 0)

    def init_sequence(self):
        """ Initialization sequence. """
        print('Reset sequence activated')
        self.write_reset()
        self.write_poll()
        self.write_setup()
        self.write_tube_status()
        self.write_coin_type()

    def run(self):
        """ Run method for the thread. """

        # First run.
        # Must not reset and start the initialization sequence.
        while 1:
            self.must_reset = False
            self.init_sequence()
            while not self.must_reset:
                # If we must not dispense a coin then poll the device.
                # Else, dispense the required coins.
                if not self.must_dispense:
                    self.is_polling = True
                    self.write_poll()
                    self.is_polling = False
                elif self.must_dispense:
                    self.is_polling = True
                    self.write_dispense(self.socket_receive[0], self.socket_receive[1])
                    self.is_polling = False
                    self.must_dispense = False
                    self.socket_response = 'Dispensed: {}.{}'.format(self.socket_receive[0], self.socket_receive[1])

    def __init__(self):
        """ Initialization of the thread. """
        super(ChangerThread, self).__init__()
        self.open_com()