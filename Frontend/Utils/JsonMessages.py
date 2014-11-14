__author__ = 'mgradob'

import simplejson as json


class Deserializer:
    def __init__(self):
        pass

    def get_command(self, in_json):
        data = json.loads(in_json)
        return data['command']


class Login:
    command = None
    params = None

    def __init__(self, in_json):
        data = json.loads(in_json)
        self.command = data['command']
        self.params = data['params']


class Solicit:
    command = None
    tipo_cobro = None
    area = None

    def __init__(self, in_json):
        data = json.loads(in_json)
        self.command = data['command']
        self.tipo_cobro = data['params'][0]
        self.area = data['params'][1]


class Cancel:
    command = None
    params = None

    def __init__(self, in_json):
        data = json.loads(in_json)
        self.command = data['command']
        self.params = data['params']


class Print:
    command = None
    params = None

    def __init__(self, in_json):
        data = json.loads(in_json)
        self.command = data['command']
        self.params = data['params']


class Logout:
    command = None
    params = None

    def __init__(self, in_json):
        data = json.loads(in_json)
        self.command = data['command']
        self.params = data['params']


class User:
    data = {
        'command': 'USER',
        'params': {
            'registrado': '',
            'tipo': '',
            'nombre': '',
            'matricula': '',
            'locker': '',
            'area': '',
            'entrega': '',
            'pago': ''
        }
    }

    def __init__(self, registrado=None, tipo=None, nombre=None, matricula=None, locker=None, area=None, entrega=None, pago=None):
        self.data['params']['registrado'] = str(registrado)
        self.data['params']['tipo'] = str(tipo)
        self.data['params']['nombre'] = str(nombre)
        self.data['params']['matricula'] = str(matricula)
        self.data['params']['locker'] = str(locker)
        self.data['params']['area'] = str(area)
        self.data['params']['entrega'] = str(entrega)
        self.data['params']['pago'] = str(pago)

    def get_json(self):
        return json.dumps(self.data)


class Confirm:
    data = {
        'command': 'CONFIRM',
        'params': {
            'inicio': '',
            'termino': '',
            'locker': '',
            'total': '',
        }
    }

    def __init__(self, inicio=None, termino=None, locker=None, area=None, total=None):
        self.data['params']['inicio'] = str(inicio)
        self.data['params']['termino'] = str(termino)
        self.data['params']['locker'] = str(locker)
        self.data['params']['total'] = str(total)

    def get_json(self):
        return json.dumps(self.data)


class Deposit:
    data = {
        'command': 'DEPOSIT',
        'params': {
            'cantidad': ''
        }
    }

    def __init__(self, cantidad=None):
        self.data['params']['cantidad'] = cantidad

    def get_json(self):
        return json.dumps(self.data)


class Paid:
    data = {
        'command': 'PAID',
        'params': {
        }
    }

    def __init__(self):
        pass

    def get_json(self):
        return json.dumps(self.data)