__author__ = 'ardzoht'

import threading
from  VMC.Bill_Dispenser import BillValidator_Thread
from VMC.Utils import Commands
import socket
import serial
import logging


class ValidatorTesting(threading.Thread):

    global serial_port

    balance = 70
    sum = 0
    try:
        serial_port = serial.Serial('COM5', 115200, timeout=1, parity=serial.PARITY_NONE)
        logging.info('Serial port open')
    except serial.SerialException:
        logging.info('Port not created')

    if serial_port.isOpen():
        serial_port.close()

    serial_port.open()

    bill_thread = BillValidator_Thread.BillValidator(serial_port)
    bill_thread.start()

    while sum < balance:

        if sum >= balance:
            break

        try:
            deposit = bill_thread.socket_com('ACCEPTBILL {}'.format(balance))
        except ValueError as ex:
            print ex

        if deposit != 0:
            sum += deposit
            logging.info('VMC: Deposit: {}, Balance: {}'.format(deposit, sum))