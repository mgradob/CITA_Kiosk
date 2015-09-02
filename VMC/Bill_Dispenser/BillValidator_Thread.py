__author__ = 'ardzoht'

import serial
from threading import Thread
from VMC.Utils import Commands
import time
import logging


class ReadThread(Thread):
    #Bill information
    deposited_20, deposited_50, deposited_100, deposited_200 = False, False, False, False
    validator_ok = False

    #Balance information
    balance = 0
    bill_count = 0

    #Flags
    must_accept = False
    must_reset = False
    first_run = False

    logging.basicConfig(level=logging.INFO)

    def __init__(self, thread_id, name):
        Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name

    def run(self):
            logging.info('Starting thread: ' + self.name)

    def reading(self):
        read, reading = True, ''

        while read:
            try:
                """
                NOTE:
                Check how is the reading handled.
                """
                data = serial_port.read()
                str_data = str(data)
                logging.info(str_data)
                if str_data == '<':
                    logging.info('Received: {}'.format(reading))

                    if reading[:6] == 'B_STA_':
                        self.validator_ok = True
                        logging.info('Validator Status --> OK')

                    elif reading[2:-1] == 'BAC_FF80':
                        self.deposited_20 = True
                        logging.info('Validator READER -> $20 Deposited')

                    elif reading[2:-1] == 'BAC_FF81':
                        self.deposited_50 = True
                        logging.info('Validator READER -> $50 Deposited')

                    elif reading[2:-1] == 'BAC_FF82':
                        self.deposited_100 = True
                        logging.info('Validator READER -> $100 Deposited')

                    elif reading[2:-1] == 'BAC_FF83':
                        self.deposited_200 = True
                        logging.info('Validator READER -> $200 Deposited')

                    reading = ''

                else:
                    reading += data

            except serial.SerialException:
                logging.error('Reader: There has been an error with the validator.')


class WriteThread(Thread):

    thread_id = None
    name = None

    bill_commands = Commands.BillCommands()

    def __init__(self, thread_id, name):
        Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name

    def write_cmd(self, cmd=Commands.BillCommands(), in_waiting=1, sleep_thread=0.1):

        # TRY to open the serial port. Check if it's open
        try:
            if serial_port.isOpen():
                # Write the requested command
                serial_port.write(cmd['request'])
                logging.info('Sent: {} cmd'.format(cmd['name']))

        except serial.SerialException:
            logging.error('Exception, data not written')

        time.sleep(0.5)

    #Bill Validator Commands
    def write_status(self):
        self.write_cmd(self.bill_commands.BILL_STATUS, 4, 0.1)

    def write_disable_all(self):
        self.write_cmd(self.bill_commands.BILL_DISABLE_ALL)

    def write_enable_all(self):
        self.write_cmd(self.bill_commands.BILL_ENABLE_20)
        self.write_cmd(self.bill_commands.BILL_ENABLE_50)


class BillValidator(Thread):

    read_thread = ReadThread(1, 'Reader')
    write_thread = WriteThread(2, 'Writer')
    commands = Commands.BillCommands()

    def start_validator(self):
        """
        Sends commands to update validator
        :return:
        """
        self.write_thread.write_disable_all()
        self.write_thread.write_status()

    def write_accept(self):
        logging.info('Accepting bills')

        if not(self.read_thread.deposited_20 or self.read_thread.deposited_50 or
               self.read_thread.deposited_100 or self.read_thread.deposited_200):
            pass

        elif self.read_thread.deposited_20:
            self.read_thread.deposited_20 = False
            return 20.0

        elif self.read_thread.deposited_50:
            self.read_thread.deposited_50 = False
            return 50.0

        elif self.read_thread.deposited_100:
            self.read_thread.deposited_100 = False
            return 100.0

        elif self.read_thread.deposited_200:
            self.read_thread.deposited_200 = False
            return 200.0

        else:
            return 0.0

    def socket_com(self, command=''):
        cmd, param = command.split()

        if cmd == 'ACCEPTBILL':
            logging.info('Command accept for bill enabled')
            return self.write_accept()

        else:
            pass

    def __init__(self, universal_port):
        global serial_port
        serial_port = universal_port
        super(BillValidator, self).__init__(universal_port)

    def run(self):
        logging.info('Starting serial port')
        self.read_thread.start()
        self.start_validator()

