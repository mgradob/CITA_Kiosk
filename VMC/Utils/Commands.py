__author__ = 'Miguel'


class VmcCommands:
    """
     Class for the VMC supported commands.
      Calculates checksum and implements methods for dispensing N quantity of
      $0.50c, $1, $2, $5 (Changer) and $10 coins (Hopper).
    """

    """ Changer Commands """
    ACK = {'cmd': 'X00<', 'name': 'ACK'}
    RESET = {'cmd': 'X0808<', 'name': 'RESET'}
    SETUP = {'cmd': 'X0909<', 'name': 'SETUP'}
    TUBE_STATUS = {'cmd': 'X0A0A<', 'name': 'TUBE_STATUS'}
    POLL = {'cmd': 'X0B0B<', 'name': 'POLL'}
    COIN_TYPE = {'cmd': 'X0C001F001F4A<', 'name': 'COIN_TYPE'}
    DISPENSE = {'cmd': '', 'name': 'DISPENSE'}

    """ Hopper Commands """
    DISPENSE_10 = {'cmd': '', 'name': 'DISPENSE_10'}

    """ Bill Dispenser Commands """
    BILL_STATUS = {'cmd': chr(182), 'name': 'BILL_STATUS'}
    BILL_ENABLE_ALL = {'cmd': chr(184), 'name': 'BILL_ENABLE_ALL'}
    BILL_ENABLE_ESCROW = {'cmd': chr(170), 'name': 'BILL_ENABLE_ESCROW'}
    BILL_DISABLE_ESCROW = {'cmd': chr(171), 'name': 'BILL_DISABLE_ESCROW'}
    BILL_ACCEPT_ESCROW = {'cmd': chr(172), 'name': 'BILL_ACCEPT_ESCROW'}
    BILL_REJECT_ESCROW = {'cmd': chr(173), 'name': 'BILL_REJECT_ESCROW'}

    """ Changer Methods """
    def dispense(self, number_of_coins, coin_type):
        """
         Creates the command used to dispense N quantity of X type of coins.
          Sent to the Changer only.
        """
        # Get HEX of number and type of coins.
        number_of_coins_hex = hex(number_of_coins).split('x')[1]
        coin_type_hex = hex(coin_type).split('x')[1]

        # Get checksum, create command, return command.
        chk = self.get_checksum([0x0D, number_of_coins << 4 | coin_type])
        self.DISPENSE['cmd'] = 'X0D{}{}{}<'.format(number_of_coins_hex, coin_type_hex, chk)
        return self.DISPENSE

    def get_checksum(self, data):
        """ Calculates the checksum of the command. """
        checksum = 0

        for num in data:
            checksum += int(num)

        return hex(checksum)[-2:].upper()

    """ Hopper Methods """
    def dispense_10(self, number_of_coins):
        """
         Creates the command used to dispense N quantity of $10 coins.
          Sent to the Hopper only.
        """
        self.DISPENSE_10['cmd'] = 'H{}<'.format(number_of_coins)
        return self.DISPENSE_10

    """ Class __init()__ method """
    def __init__(self):
        """ Initialization method. """
        pass