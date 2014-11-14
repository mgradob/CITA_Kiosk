__author__ = 'mgradob'

""" Imports """
import threading
import serial
from VMC.Utils import Commands, Tubes
from time import sleep


class ReadThread(threading.Thread):

    deposited_50c, deposited_1, deposited_2, deposited_5 = False, False, False, False
    available_50c, available_1, available_2, available_5 = 0, 0, 0, 0
    tubes = Tubes.Tubes()

    def __init__(self, thread_id, name):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name

    def run(self):
        print 'Starting thread: ' + self.name
        self.reading()

    def reading(self):
        read, reading = True, ''

        while read:
            try:
                data = serial_port.read()
                str_data = str(data)

                if str_data == '<':
                    print 'Received: {}'.format(reading)

                    if reading[:-2] == 'C_CDM_50':
                        available_50c = int(reading[-2:])
                        print 'READER: 1 coin $0.5, in tube: {}'.format(available_50c)
                        self.deposited_50c = True

                    elif reading[:-2] == 'C_CDM_52':
                        available_1 = int(reading[-2:])
                        print 'READER: 1 coin $1.0, in tube: {}'.format(available_1)
                        self.deposited_1 = True

                    elif reading[:-2] == 'C_CDM_53':
                        available_2 = int(reading[-2:])
                        print 'READER: 1 coin $2.0, in tube: {}'.format(available_2)
                        self.deposited_2 = True

                    elif reading[:-2] == 'C_CDM_54':
                        available_5 = int(reading[-2:])
                        print 'READER: 1 coin $5.0, in tube: {}'.format(available_5)
                        self.deposited_5 = True

                    elif reading[:6] == 'C_TUB_':
                        self.tubes.full_tubes = reading[7:10]
                        self.tubes.tube_50c = int(reading[11:12])
                        self.tubes.tube_1 = int(reading[13:16])
                        self.tubes.tube_2 = int(reading[17:18])
                        self.tubes.tube_5 = int(reading[19:20])

                        print 'READER: Full tubes: {}'.format(self.tubes.full_tubes)
                        print 'READER: Coins on tube_50c: {}'.format(self.tubes.tube_50c)
                        print 'READER: Coins on tube_1: {}'.format(self.tubes.tube_1)
                        print 'READER: Coins on tube_2: {}'.format(self.tubes.tube_2)
                        print 'READER: Coins on tube_5: {}'.format(self.tubes.tube_5)

                    reading = ''
                else:
                    reading += data

            except serial.SerialException:
                print 'Reader: Error, exception'


class WriteThread(threading.Thread):
    def __init__(self, thread_id, name):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name

    def write_cmd(self, cmd=Commands.VmcCommands()):
        try:
            if serial_port.isOpen():
                serial_port.write(cmd['request'])
                print 'Sent: {} cmd'.format(cmd['name'])

        except serial.SerialException:
            print 'Exception, data not written'

        sleep(0.5)


class Changer(threading.Thread):

    read_thread = ReadThread(1, 'Reader')
    write_thread = WriteThread(2, 'Writer')
    commands = Commands.VmcCommands()

    def start_serial(self):
        try:
            global serial_port

            # TODO Change serial port to the uC's.
            serial_port = serial.Serial('/dev/tty.usbserial-FTDBL0IK', 115200, timeout=1, parity=serial.PARITY_NONE)
            self.serial_port = serial_port
            print 'Serial port open'
        except serial.SerialException:
            print 'Port not created'

        if serial_port.isOpen():
            serial_port.close()

        serial_port.open()

    def start_changer(self):
        self.write_thread.write_cmd(self.commands.C_SETUP)
        self.write_thread.write_cmd(self.commands.C_TUBE_STATUS)
        self.write_thread.write_cmd(self.commands.C_EXPANSION)
        self.write_thread.write_cmd(self.commands.disable_tubes())

    def write_dispense(self, units=0, cents=0):
            """ Writes a Dispense command. Also evaluates which coins should be dispensed. """
            # Evaluate coins.
            res = int(units)
            quantity_10 = res / 10
            res %= 10
            quantity_5 = res / 5
            res %= 5
            quantity_2 = res / 2
            res %= 2
            quantity_1 = res / 1

            quantity_50c = int(cents) / 5

            # Dispense coins depending on the coins it should dispense.
            self.write_thread.write_cmd(self.commands.enable_tubes())

            if not quantity_10 == 0:
                self.write_thread.write_cmd(self.commands.hopper_dispense(quantity_10))

            if not quantity_5 == 0:
                self.write_thread.write_cmd(self.commands.changer_dispense(4, quantity_5))

            if not quantity_2 == 0:
                self.write_thread.write_cmd(self.commands.changer_dispense(3, quantity_2))

            if not quantity_1 == 0:
                self.write_thread.write_cmd(self.commands.changer_dispense(2, quantity_1))

            if not quantity_50c == 0:
                self.write_thread.write_cmd(self.commands.changer_dispense(0, quantity_50c))

            self.write_thread.write_cmd(self.commands.disable_tubes())

    def write_accept(self):
        self.write_thread.write_cmd(self.commands.enable_tubes())

        while (not self.read_thread.deposited_50c) and (not self.read_thread.deposited_1) and (not self.read_thread.deposited_2) and (not self.read_thread.deposited_5):
            pass

        print 'Coin deposited'
        self.write_thread.write_cmd(self.commands.disable_tubes())

        if self.read_thread.deposited_50c:
            self.read_thread.deposited_50c = False
            return 0.5

        elif self.read_thread.deposited_1:
            self.read_thread.deposited_1 = False
            return 1.0

        elif self.read_thread.deposited_2:
            self.read_thread.deposited_2 = False
            return 2.0

        elif self.read_thread.deposited_5:
            self.read_thread.deposited_5 = False
            return 5.0

        else:
            return 0

    def socket_com(self, command=''):
        cmd, param1 = command.split()

        if cmd == 'DISPENSE':
            units, cents = param1.split('.')
            self.write_dispense(units, cents)

            return 'OK'

        elif cmd == 'ACCEPT':
            return self.write_accept()

        else:
            pass

    def __init__(self):
        super(Changer, self).__init__()

    def run(self):
        print 'Starting serial port'
        self.start_serial()

        print 'Starting threads'
        self.read_thread.start()
        self.start_changer()