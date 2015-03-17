__author__ = 'mario_000'

""" Imports """
from VMC.Utils import Commands

import serial
import threading
from time import sleep


class PrinterThread(threading.Thread):
    """
    Class PrinterThread
        Thread connection with the printer

    """

    """ Global Variables """
    # COM variables
    com_port = None

    # Commands and VMCCommands object
    commands = Commands.VmcCommands()

    # Flags
    is_printing = False
    printer_ready = False
    must_reset = False
    must_accept = False
    first_run = False

    #Ticket Parameters
    user = ""
    folio = ""
    date = ""
    place = ""
    hour = ""
    start_hour = ""
    end_hour = ""
    state = ""
    scheme = ""
    total = ""

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

        self.com_port = serial.Serial('/dev/cu.usbserial', 115200,
                                      parity=serial.PARITY_NONE)

        if self.com_port.isOpen():
            self.com_port.close()
        self.com_port.open()
        print('{} is open.'.format(self.com_port.name))

    def set_ticker_parameters(self, user, folio, date, place, hour, start_hour,
                              end_hour, state, scheme, total):
        self.user = user
        self.folio = folio
        self.date = date
        self.place = place
        self.hour = hour
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.state = state
        self.scheme = scheme
        self.total = total

    def print_ticket(self, sleep_thread=0.25):
        """
         Method for sending a command via serial port.
          Defaults: waits for 1 byte on the serial buffer, sleeps the thread for 100ms.
        """

        # Try to open the serial port. First check if it's open already.
        try:
            if self.com_port.isOpen():
                self.com_port.write("""
                    ^XA~TA000~JSB^LT0^MNV^MTD^PON^PMN^LH0,0^JMA^PR4,4~SD20^JUS^LRN^CI0^XZ
                """)

                self.com_port.write("""
                    ^XA
                    ^MMK
                    ^KV0,9,0,0,400
                    ^CN1
                    ~PL000
                    ^PN0
                    ^PW607
                    ^LL10^LS0
                    ^FO50,50^XGE:SALTOLOC.GRF,1,1^FS
                    ^FT0,201^XG000.GRF,1,1^FS
                    ^FO8,30^GB592,0,12^FS
                    ^FO58,678^GB488,0,8^FS
                    ^FT17,240^A0N,28,28^FH\^FDFOLIO: """ + self.folio + """^FS
                    ^FT17,265^A0N,28,28^FH\^FDUSUARIO:""" + self.user + """^FS
                    ^FT337,548^A0N,110,112^FH\^FD""" + self.place + """^FS
                    ^FT327,591^A0N,11,14^FH\^F""" + self.place + """^FS
                    ^FT17,347^A0N,20,19^FH\^FDHORA DE FIN": """ + self.end_hour + """^FS
                    ^FT17,367^A0N,20,19^FH\^FDHORA DE INICIO: """ + self.start_hour + """^FS
                    ^FT315,437^A0N,20,19^FH\^FDLOCKER """ + self.state + """^FS
                    ^FT44,500^A0N,14,14^FH\^FDESQUEMA DE RENTA: """ + self.scheme + """^FS
                    ^FT44,540^A0N,20,20^FH\^FDTOTAL: $""" + self.total + """^FS
                    ^FT189,639^A0N,20,19^FB191,1,0,C^FH\^FDGRACIAS POR UTILIZAR^FS
                    ^FT189,663^A0N,20,19^FB191,1,0,C^FH\^FDSALTO LOCKERS^FS
                    ^PQ1,0,1,Y^XZ
                """)
                self.com_port.write("""^XA^ID000.GRF^FS^XZ""")


                # Sleep the thread until we have the minimum required data or until we have a timeout (default=500ms).
                """
                timeout = 0
                while self.com_port.inWaiting() < in_waiting and timeout < 5:
                    timeout += 1
                    sleep(.1)
                if timeout >= 5:
                    raise serial.SerialException
                """
                self.com_port.flushInput()
                self.com_port.flushOutput()


        except serial.SerialException:
            # If a SerialException is catch then must restart the communication.
            self.must_reset = True
            sleep(sleep_thread)
            print "Fallo"
            return ''

    def run(self):
        while True:
            if self.printer_ready:
                self.print_ticket()
                self.printer_ready=False


    def __init__(self):
        """ Initialization of the thread. """
        super(PrinterThread, self).__init__()
        self.open_com()