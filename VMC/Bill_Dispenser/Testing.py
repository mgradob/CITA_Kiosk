__author__ = 'ardzoht'

import threading
from  VMC.Bill_Dispenser import BillValidator_Thread
from VMC.Utils import Commands
import socket
import serial
import logging
from time import sleep
from VMC import VmcController


class Testing(threading.Thread):

    global serial_port

    balance = 70
    sum = 0
    try:
        serial_port = serial.Serial('/dev/cu.usbserial-FTVSGL58', 115200, timeout=1, parity=serial.PARITY_NONE)
        logging.info('Serial port open')
    except serial.SerialException:
        logging.info('Port not created')

    if serial_port.isOpen():
        serial_port.close()

    serial_port.open()

    bill_thread = BillValidator_Thread.BillValidator(serial_port)
    bill_thread.start()
    sleep(5)
    bill_thread.write_thread.write_enable_all()
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

"""
class Testing(threading.Thread):

    vmc = VmcController.VmcController('localhost', 1025, 1)
    vmc.start()
    vmc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock_status = vmc_socket.connect_ex(('localhost', 1025))
    sleep(4)
    vmc_socket.sendall('ACCEPT 20')
    logging.info('SOCKET STATUS {}'.format(sock_status))

    try:
        while True:
            socket_data_in = vmc_socket.recv(1024)

            if socket_data_in == 'CANCEL':
                logging.info('Cancelled')
                break

            if socket_data_in == 'COMPLETE':
                logging.info('Completed')
                break
    except Exception as ex:
        logging.info('ERROR {}'.format(ex))
"""