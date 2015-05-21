__author__ = 'mgradob'

""" Imports """
import threading
import serial
from VMC.Utils import Commands, Tubes
import time

class ReadThread(threading.Thread):

    deposited_50c, deposited_1, deposited_2, deposited_5, deposited_10 = False, False, False, False, False
    available_50c, available_1, available_2, available_5 = 0, 0, 0, 0
    tubes = Tubes.Tubes()
    hopper_ok = False
    dispense_error = False

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
                # print str_data
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

                    elif reading[:-2] == 'C_CDM_45':
                        print 'READER: 1 coin $10.0 deposited to hopper'
                        self.deposited_10 = True

                    elif reading[:6] == 'C_TUB_':
                        self.tubes.full_tubes = reading[7:10]
                        self.tubes.tube_50c = int(reading[11:12])
                        self.tubes.tube_1 = int(reading[13:16])
                        self.tubes.tube_2 = int(reading[17:18])
                        self.tubes.tube_5 = int(reading[19:20])

                    #Check for hopper availability
                    elif reading == 'H_STA_OK<':
                        self.hopper_ok = True

                    elif reading == 'H_STA_ERROR<':
                        self.hopper_ok = False
                        print 'READER: Full tubes: {}'.format(self.tubes.full_tubes)
                        print 'READER: Coins on tube_50c: {}'.format(self.tubes.tube_50c)
                        print 'READER: Coins on tube_1: {}'.format(self.tubes.tube_1)
                        print 'READER: Coins on tube_2: {}'.format(self.tubes.tube_2)
                        print 'READER: Coins on tube_5: {}'.format(self.tubes.tube_5)

                    #Check for Hopper/Changer error responses
                    elif reading[:-2] == 'H_DIS_TIMEOUT_':
                        self.dispense_error = True

                    elif reading[:-1] == 'C_DIS_ERROR':
                        self.dispense_error = True
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

        time.sleep(0.5)

class Changer(threading.Thread):

    read_thread = ReadThread(1, 'Reader')
    write_thread = WriteThread(2, 'Writer')
    commands = Commands.VmcCommands()
    number_of_coins = 100 #dummy data for coins on hopper
    error_amount = 0
    
    def start_serial(self):
        try:
            global serial_port

            # TODO Change serial port to the uC's.
            #Lo cambie para poder conectar la impresora en el COM6
            serial_port = serial.Serial('COM9', 115200, timeout=1, parity=serial.PARITY_NONE)
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
            #Check tubes status
            self.write_thread.write_cmd(self.commands.C_TUBE_STATUS)
            #Get available coins on each tube
            av_50c = self.read_thread.tubes.tube_50c
            print "Available 50c = " + av_50c
            av_1 = self.read_thread.tubes.tube_1
            print "Available 1 = " + av_1
            av_2 = self.read_thread.tubes.tube_2
            print "Available 2 = " + av_2
            av_5 = self.read_thread.tubes.tube_5
            print "Available 5 = " + av_5

            if quantity_10 != 0 and quantity_10 <= self.number_of_coins:
                print "Dispensing Hopper coins = " + str(quantity_10)
                self.write_thread.write_cmd(self.commands.check_hopper())
                self.write_thread.write_cmd(self.commands.hopper_dispense(quantity_10))
                self.number_of_coins -= quantity_10
            elif quantity_10 != 0 and quantity_10 > self.number_of_coins:
                self.error_amount += quantity_10*10
                self.read_thread.dispense_error = True
            if quantity_5 != 0 and quantity_5 <= av_5:
                print "Dispensing Changer coins = " + str(quantity_5)
                self.write_thread.write_cmd(self.commands.changer_dispense(4, quantity_5))
            elif quantity_5 != 0 and quantity_2 > av_5:
                self.error_amount += quantity_5*5
                self.read_thread.dispense_error = True
            if quantity_2 != 0 and quantity_2 <= av_2:
                print "Dispensing Changer coins = " + str(quantity_2)
                self.write_thread.write_cmd(self.commands.changer_dispense(3, quantity_2))
            elif quantity_2 != 0 and quantity_2 > av_2:
                self.error_amount += quantity_2*2
                self.read_thread.dispense_error = True
            if quantity_1 != 0 and quantity_1 <= av_1:
                print "Dispensing Changer coins = " + str(quantity_1)
                self.write_thread.write_cmd(self.commands.changer_dispense(2, quantity_1))
            elif quantity_1 != 0 and quantity_1 > av_1:
                self.error_amount += quantity_1
                self.read_thread.dispense_error = True
            if quantity_50c != 0 and quantity_50c <= av_50c:
                print "Dispensing Changer coins = " + str(quantity_50c)
                self.write_thread.write_cmd(self.commands.changer_dispense(0, quantity_50c))
            elif quantity_50c != 0 and quantity_50c > av_50c:
                self.error_amount += quantity_50c*.5
                self.read_thread.dispense_error = True

            self.write_thread.write_cmd(self.commands.disable_tubes())

    def write_accept(self):
        self.write_thread.write_cmd(self.commands.enable_tubes())

        if(not self.read_thread.deposited_50c) and (not self.read_thread.deposited_1) \
                and (not self.read_thread.deposited_2) and (not self.read_thread.deposited_5)\
                and (not self.read_thread.deposited_10):
            pass
            time.sleep(1)
        

        print 'Coin deposited'
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

        elif self.read_thread.deposited_10:
            self.read_thread.deposited_10 = False
            return 10.0

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