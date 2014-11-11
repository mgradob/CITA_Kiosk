__author__ = 'mgradob'

import json


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
    command = None
    params = []
    data = []

    def __init__(self, registrado=None, tipo=None, nombre=None, matricula=None, locker=None, area=None, entrega=None, pago=None):
        self.command = 'USER'
        self.params.append(registrado)
        self.params.append(tipo)
        self.params.append(nombre)
        self.params.append(matricula)
        self.params.append(locker)
        self.params.append(area)
        self.params.append(entrega)
        self.params.append(pago)

        self.data = [self.command, self.params]

    def get_json(self):
        return json.dumps(self.data, default=lambda o: o.__dict__, sort_keys=False, indent=4)


class Confirm:
    command = None
    params = []
    data = []

    def __init__(self, inicio=None, termino=None, locker=None, area=None, total=None):
        self.command = 'CONFIRM'
        self.params.append(inicio)
        self.params.append(termino)
        self.params.append(locker)
        self.params.append(area)
        self.params.append(total)

        self.data = [self.command, self.params]

    def get_json(self):
        return json.dumps(self.data, default=lambda o: o.__dict__, sort_keys=False, indent=4)


class Deposit:
    command = None
    params = []
    data = []

    def __init__(self, cantidad=None):
        self.command = 'DEPOSIT'
        self.params.append(cantidad)

        self.data = [self.command, self.params]

    def get_json(self):
        return json.dumps(self.data, default=lambda o: o.__dict__, sort_keys=False, indent=4)


class Paid:
    command = None
    params = ''
    data = []

    def __init__(self):
        self.command = 'PAID'

        self.data = [self.command, self.params]

    def get_json(self):
        return json.dumps(self.data, default=lambda o: o.__dict__, sort_keys=False, indent=4)