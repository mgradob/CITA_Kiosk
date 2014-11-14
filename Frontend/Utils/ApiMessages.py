__author__ = 'mgradob'

import json
import datetime
import requests
import Models
from requests.auth import HTTPBasicAuth

base_url = 'http://localhost:8080/'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}


class User:
    uid = None
    user = None

    def __init__(self, uid=None):
        self.uid = uid

    def get_user_data(self):
        r = requests.get(base_url + 'Users/' + self.uid)
        data = json.loads(r.content)

        self.user = Models.UserModel(
            data['user_id'],
            data['user_name'],
            data['user_ap'],
            data['user_am'],
            data['user_matricula'],
            data['user_discount']
        )

    def get_user(self):
        self.get_user_data()
        return self.user


class Lockers:
    lockers_list = []
    areas_list = []

    def __init__(self):
        self.get_lockers()
        self.get_areas()

    def get_lockers(self):
        for locker in requests.get(base_url + 'Lockers/').json():
            self.lockers_list.append(Models.LockerModel(
                locker['locker_id'],
                locker['locker_name'],
                locker['locker_match'],
                locker['locker_status'],
                locker['locker_start_time'],
                locker['fk_area'],
                locker['fk_user']
            ))

    def get_areas(self):
        for area in requests.get('http://localhost:8000/Areas/').json():
            self.areas_list.append(Models.AreaModel(
                area['area_id'],
                area['area_name'],
                area['area_description'],
                area['area_enable']
            ))

    def get_available_lockers(self):
        available = []
        for locker in self.lockers_list:
            if locker.fk_user is None:
                available.append(locker)
        return available

    def has_assigned_locker(self, user):
        for locker in self.lockers_list:
            if locker.fk_user is not None:
                if user == locker.fk_user.split('Users/')[1][:-1]:
                    return True
        return False

    def assign_locker(self, user_id, locker, area_id, start_date):
        r = requests.delete('{}Lockers/{}'.format(base_url, locker.locker_id), auth=HTTPBasicAuth('admin', 'admin'))
        print 'Deletion of locker: {}'.format(r.status_code)

        payload = {
            "locker_id": locker.locker_id,
            "locker_name": locker.locker_name,
            "locker_match": "True",
            "locker_status": "In Use",
            "locker_start_time": start_date,
            "fk_area": '{}'.format(locker.fk_area),
            "fk_user": "http://localhost:8080/Users/{}/".format(user_id)
        }

        r = requests.post('{}Lockers/'.format(base_url), data=payload, auth=HTTPBasicAuth('admin', 'admin'))
        print 'Locker assignation: '.format(r.status_code)