__author__ = 'mgradob'

import requests, json
import Models

base_url = 'http://localhost:8000/'


class User:
    uid = None
    user = None

    def __init__(self, uid=None):
        self.uid = uid

    def get_user_data(self):
        r = requests.get(base_url + 'Users/' + self.uid)
        data = json.loads(r.content)

        self.user = Models.UserModel(data['user_id'], data['user_name'], data['user_ap'], data['user_am'], data['user_matricula'], data['user_discount'])

    def get_user(self):
        self.get_user_data()
        return self.user


class Lockers:
    lockers_list = []

    def __init__(self):
        pass

    def get_lockers(self):
        for locker in requests.get('http://localhost:8000/Lockers/').json():
            self.lockers_list.append(locker['fk_user'][-9:-1])

    def has_assigned_locker(self, user):
        if self.lockers_list.__contains__(user):
            return True
        else:
            return False