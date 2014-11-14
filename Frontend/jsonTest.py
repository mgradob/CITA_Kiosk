__author__ = 'mgradob'

import datetime, simplejson as json
from Utils import JsonMessages

# mJson = '{"command": "SOLICIT", "params": ["SEMESTER", "in_prep"]}'
#
# login_m = JsonMessages.Solicit(mJson)
# print login_m.command
# print login_m.tipo_cobro
# print login_m.area
#
# user = JsonMessages.User('No', 'SEMESTER', 'Miguel Grado Baylon', 'A0075845', 'A1', 'Prep', str(datetime.datetime.now()), '50')
# print user.get_json()
#
# confirm = JsonMessages.Confirm(str(datetime.datetime.now()), str(datetime.datetime.now()), 'A1', 'Prep', '50')
# print confirm.get_json()
#
# deposit = JsonMessages.Deposit('50')
# print deposit.get_json()
#
# paid = JsonMessages.Paid()
# print paid.get_json()

class User:
    command = None
    params = []
    data = []

    json_data = {
        'command': None,
        'params': {
            'registrado': None,
            'tipo': None,
            'nombre': None,
            'matricula': None,
            'locker': None,
            'area': None,
            'entrega': None,
            'pago': None
        }
    }

    def __init__(self, registrado=None, tipo=None, nombre=None, matricula=None, locker=None, area=None, entrega=None, pago=None):
        self.command = 'USER'
        self.json_data['command'] = 'USER'
        self.json_data['params']['registrado'] = registrado
        self.json_data['params']['tipo'] = tipo
        self.json_data['params']['nombre'] = nombre
        self.json_data['params']['matricula'] = matricula
        self.json_data['params']['locker'] = locker
        self.json_data['params']['area'] = area
        self.json_data['params']['entrega'] = entrega
        self.json_data['params']['pago'] = pago

    def get_json(self):
        return json.dumps(self.json_data)

user = User('No', 'SEMESTRE', 'Miguel Grado', 'A0075845', 1, 'CITA', str(datetime.datetime.now()), 50)
print user.get_json()