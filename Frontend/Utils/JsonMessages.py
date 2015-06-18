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


class ChangeLockerStatus:
    command = None
    locker_id= None
    status = None

    def __init__(self, in_json):
        data = json.loads(in_json)
        self.command = data['command']
        self.locker_id = data['params'][0]
        self.status = data['params'][1]


class OkAvailable:
    command = None
    rent_type = None
    added_payment = None

    def __init__(self, in_json):
        data = json.loads(in_json)
        self.command = data['command']
        self.rent_type = data['params'][0]
        self.added_payment = data['params'][1]


class Cancel:
    command = None
    params = None

    def __init__(self, in_json):
        data = json.loads(in_json)
        self.command = data['command']
        self.params = data['params']


class GetLog:
    command = None
    params = None
    month = None

    def __init__(self, in_json):
        data = json.loads(in_json)
        self.command = data['command']
        self.params = data['params']
        self.month = data['params'][1]


class GetMoney:
    command = None
    params = None
    cantidad = None

    def __init__(self, in_json):
        data = json.loads(in_json)
        self.command = data['command']
        self.cantidad= data['params'][0]


class Print:
    command = None
    params = None
    user = None
    start_date = None
    end_date = None
    end_time = None
    rent_type = None
    locker_id = None
    total = None
    numeration = None

    def __init__(self, in_json):
        data = json.loads(in_json)
        self.command = data['command']
        self.params = data['params']
        self.user = data['params'][0]
        self.start_date = data['params'][1]
        self.end_date = data['params'][2]
        self.end_time = data['params'][3]
        self.rent_type = data['params'][4]
        self.locker_id = data['params'][5]
        self.total = data['params'][6]
        self.numeration = data['params'][7]

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
            'pago': '',
            'balance': ''
        }
    }

    def __init__(self, registrado=None, tipo=None, nombre=None, matricula=None, locker_id=None,
                 locker =None, locker_confirmado=None, area=None, inicio=None, entrega=None, pago=None, balance=None):
        self.data['params']['registrado'] = str(registrado)
        self.data['params']['tipo'] = str(tipo)
        self.data['params']['nombre'] = str(nombre)
        self.data['params']['matricula'] = str(matricula)
        self.data['params']['locker'] = str(locker)
        self.data['params']['locker_id'] = str(locker_id)
        self.data['params']['locker_confirmado'] = str(locker_confirmado)
        self.data['params']['area'] = str(area)
        self.data['params']['inicio'] = str(inicio)
        self.data['params']['entrega'] = str(entrega)
        self.data['params']['pago'] = str(pago)
        self.data['params']['balance'] = str(balance)

    def get_json(self):
        return json.dumps(self.data)


class Confirm:
    data = {
        'command': 'CONFIRM',
        'params': {
            'inicio': '',
            'termino': '',
            'locker': '',
            'total': ''
        }
    }

    def __init__(self, inicio=None, termino=None, locker=None, total=None, periodo=None):
        self.data['params']['inicio'] = str(inicio)
        self.data['params']['termino'] = str(termino)
        self.data['params']['locker'] = str(locker)
        self.data['params']['total'] = str(total)
        self.data['params']['periodo'] = str(periodo)

    def get_json(self):
        return json.dumps(self.data)


class Difference:
    data = {
        'command': 'DIFFERENCE',
        'params': {
            'cantidad': ''
        }
    }

    def __init__(self, cantidad=None):
        self.data['params']['cantidad'] = str(cantidad)

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
        self.data['params']['cantidad'] = str(cantidad)

    def get_json(self):
        return json.dumps(self.data)


class Timeout:
    data = {
        'command': 'TIMEOUT',
        'params': {
            'cantidad': ''
        }
    }

    def __init__(self, cantidad=None):
        self.data['params']['cantidad'] = str(cantidad)

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

class Exit:
    data = {
        'command': 'EXIT',
        'params': {
        }
    }

    def __init__(self):
        pass

    def get_json(self):
        return json.dumps(self.data)


class Logs:
    data = {
        'command': 'Log',
        'params': {
        }
    }

    def __init__(self, log):
        self.data['params']['logs'] = log

    def get_json(self):
        return json.dumps(self.data)

class Accept:
    data = {
        'command': 'ACCEPT',
        'params': {
        }
    }

    def __init__(self):
        pass

    def get_json(self):
        return json.dumps(self.data)


class Areas:
    data = {
        'command': 'AREAS',
        'params': {
            'areas': ''
        }
    }

    def __init__(self, areas=None):
        self.data['params']['areas'] = areas

    def get_json(self):
        return json.dumps(self.data)


class Error:
    data = {
        'command': 'ERROR',
        'params': {
            'abort': '',
            'errno': '',
            'description' :''
        }
    }

    def __init__(self,abort=None, errno=None, description=None):
        self.data['params']['abort'] = str(abort)
        self.data['params']['errno'] = str(errno)
        self.data['params']['description'] = str(description)

    def get_json(self):
        return json.dumps(self.data)

class Changed:
    data = {
        'command': 'CHANGED',
        'params':{}
    }
    def __init__(self,locker=None, area=None):
        self.data['params']['locker_id'] = locker.locker_id
        self.data['params']['locker_name'] = locker.locker_name
        self.data['params']['area_id'] = area.area_id
        self.data['params']['area_name'] = area.area_name

    def get_json(self):
        return json.dumps(self.data)