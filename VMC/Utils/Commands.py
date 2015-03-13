__author__ = 'Miguel'


class VmcCommands:
    """
     Class for the VMC supported commands.
      Calculates checksum and implements methods for dispensing N quantity of
      $0.50c, $1, $2, $5 (Changer) and $10 coins (Hopper).
    """

    def __init__(self):
        pass

    """ Changer Commands (implemented on uC)"""
    """ Hopper """
    H_STATUS = {'name': 'H_STATUS', 'request': 'H_STA<'}
    # Finish H_DISPENSE command in method.
    H_DISPENSE = {'name': 'H_DISPENSE', 'request': 'H_DIS_'}
    """ Changer """
    C_POLL = {'name': 'C_POLL', 'request': 'C_POLL<'}
    C_EXP_DIAG = {'name': 'C_EXP_DIAG', 'request': 'C_STA<'}
    # Finish C_DISPENSE command in method.
    C_DISPENSE = {'name': 'C_DISPENSE', 'request': 'C_DIS_'}
    C_TUBE_STATUS = {'name': 'C_TUBE_STATUS', 'request': 'C_TUB<'}
    C_SETUP = {'name': 'C_SETUP', 'request': 'C_SUP<'}
    C_EXPANSION = {'name': 'C_EXPANSION', 'request': 'C_EID<'}
    # Finish C_COIN_TYP command in method.
    C_COIN_TYPE = {'name': 'C_COIN_TYPE', 'request': 'C_CTY_'}

    def hopper_dispense(self, quantity=1):
        data = 'H_DIS_{}<'.format(quantity)
        cmd = self.H_DISPENSE
        cmd['request'] = data
        print cmd['request']
        return cmd

    def check_hopper(self):
        cmd = self.H_STATUS
        print cmd['request']
        return cmd

    def changer_dispense(self, coin_type=0, number=0):
        data = 'C_DIS_{}{}<'.format(coin_type, number)
        cmd = self.C_DISPENSE
        cmd['request'] = data
        print cmd['request']
        return cmd

    def enable_tubes(self):
        data = 'C_CTY_{}<'.format('003F003F')
        cmd = self.C_COIN_TYPE
        cmd['request'] = data
        print cmd['request']
        return cmd

    def disable_tubes(self):
        data = 'C_CTY_{}<'.format('00000000')
        cmd = self.C_COIN_TYPE
        cmd['request'] = data
        print cmd['request']
        return cmd


class BillCommands:
    """ Bill Dispenser Commands """
    BILL_STATUS = {'cmd': chr(182), 'name': 'BILL_STATUS'}
    BILL_ENABLE_ALL = {'cmd': chr(184), 'name': 'BILL_ENABLE_ALL'}
    BILL_ENABLE_ESCROW = {'cmd': chr(170), 'name': 'BILL_ENABLE_ESCROW'}
    BILL_DISABLE_ESCROW = {'cmd': chr(171), 'name': 'BILL_DISABLE_ESCROW'}
    BILL_ACCEPT_ESCROW = {'cmd': chr(172), 'name': 'BILL_ACCEPT_ESCROW'}
    BILL_REJECT_ESCROW = {'cmd': chr(173), 'name': 'BILL_REJECT_ESCROW'}

    def __init__(self):
        """ Initialization method. """
        pass