__author__ = 'mgradob'

import json
import datetime
import requests
import Models
from requests.auth import HTTPBasicAuth

base_url = 'http://localhost:8000/'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Pragma': 'no-cache', 'Cache-control' : 'no-cache'}
#db_user = 'admin'
#db_pass = 'admin'
db_user = 'becario'
db_pass = 'becario'

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

    def __init__(self, locker = None, rent_confirmation = None):
        if locker is None:
            self.get_lockers()
            self.get_areas()
        else:
            self.confirm_assign_locker(locker,rent_confirmation)

    def get_lockers(self):
        self.lockers_list = []
        for locker in requests.get(base_url + 'Lockers/').json():
            self.lockers_list.append(Models.LockerModel(
                locker['locker_id'],
                locker['locker_name'],
                locker['locker_rent_confirmed'],
                locker['locker_rent_type'],
                locker['locker_status'],
                locker['locker_start_time'],
                locker['locker_end_time'],
                locker['fk_area'],
                locker['fk_user']
            ))

    def get_areas(self):
        self.areas_list = []
        for area in requests.get(base_url + 'Areas/').json():
            self.areas_list.append(Models.AreaModel(
                area['area_id'],
                area['area_name'],
                area['area_description'],
                area['area_enable']
            ))

    #Return Json from Request of all areas
    def get_areas_json(self):
        return requests.get(base_url + 'Areas/').json()

    def get_available_lockers(self):
        available = []
        for locker in self.lockers_list:
            print 'gal - {} {} {}'.format(locker.locker_id, locker.locker_name, locker.fk_user)
            if locker.fk_user is None:
                available.append(locker)
        return available

    # Get available lockers in area
    def get_available_lockers_area(self, area_id):
        available = []
        for locker in self.lockers_list:
            locker_area = locker.fk_area.split('Areas/')[1][:-1]
            if locker.fk_user is None and locker_area == str(area_id) and locker.locker_status == "available":
                available.append(locker)
        return available

    # Check if the user has a locker
    def has_assigned_locker(self, user):
        for locker in self.lockers_list:
            print 'hal - {} {} {}'.format(locker.locker_id, locker.locker_name, locker.fk_user)
            if locker.fk_user is not None:
                if user == locker.fk_user.split('Users/')[1][:-1]:
                    return True
        return False

    # Return the locker assigned to the user
    def has_assigned_locker_info(self, user):
        for locker in self.lockers_list:
            print 'hali - {} {} {}'.format(locker.locker_id, locker.locker_name, locker.fk_user)
            if locker.fk_user is not None:
                if user == locker.fk_user.split('Users/')[1][:-1]:
                    return locker
        return None

    def get_area_info(self, area_id_route):
        area_id = int(area_id_route.split('Areas/')[1][:-1])
        for area in self.areas_list:
            if area.area_id == area_id:
                return area
        return None

    def get_locker_info(self, locker_id):
        for locker in self.lockers_list:
            if str(locker.locker_id) == locker_id:
                return locker
        return None

    def assign_locker(self, user_id, locker, rent_type, start_date, end_date):
        #r = requests.delete('{}Lockers/{}'.format(base_url, locker.locker_id), auth=HTTPBasicAuth(db_user, db_pass))
        #print 'Deletion of locker: {}'.format(r.status_code)

        payload = {
            #"locker_id": locker.locker_id,
            #"locker_name": locker.locker_name,
            "locker_rent_confirmed": False, #"True",
            "locker_rent_type": rent_type,
            "locker_status": "in_use",
            "locker_start_time": start_date,
            "locker_end_time": end_date,
            # "fk_area": '{}'.format(locker.fk_area),
            "fk_user": base_url + "Users/{}/".format(user_id)
        }

        #r = requests.post('{}Lockers/'.format(base_url), data=payload, auth=HTTPBasicAuth(db_user, db_pass))
        #print 'Locker assignation: '.format(r.status_code)

        r = requests.patch('{}Lockers/{}/'.format(base_url,locker.locker_id), data=payload, auth=HTTPBasicAuth(db_user, db_pass))

        print 'Locker assignation: {}'.format(r.status_code)

    def confirm_assign_locker(self, locker, rent_confirmation):

        payload = {
            "locker_rent_confirmed": rent_confirmation
        }

        r = requests.patch('{}Lockers/{}/'.format(base_url,locker.locker_id), data=payload, auth=HTTPBasicAuth(db_user, db_pass))
        print 'Locker confirmation: {}'.format(r.status_code)

    def change_locker_status(self, locker_id, locker_status):

        payload = {
            "locker_status": locker_status
        }

        r = requests.patch('{}Lockers/{}/'.format(base_url, locker_id), data=payload, auth=HTTPBasicAuth(db_user, db_pass))
        print 'Locker status change: {}'.format(r.status_code)

    def test_delete_locker(self, locker):

        payload = {
            "locker_rent_confirmed": False,
            "locker_rent_type": None,
            "locker_status": "available",
            "locker_start_time": None,
            "locker_end_time": None,
            "fk_user": None
        }

        headers = {'content-type': 'application/json'}
        r = requests.patch('{}Lockers/{}/'.format(base_url, locker.locker_id), data=json.dumps(payload),
                         headers=headers, auth=HTTPBasicAuth(db_user, db_pass))
        print 'Delete change: {}'.format(r.status_code)

    def migrate_locker(self, old_locker, new_locker):

        payload_new = {
            "locker_rent_confirmed": old_locker.locker_rent_confirmed,
            "locker_rent_type": old_locker.locker_rent_type,
            "locker_status": "in_use",
            "locker_start_time": old_locker.locker_start_time,
            "locker_end_time": old_locker.locker_end_time,
            "fk_user": old_locker.fk_user
        }

        r_new = requests.patch('{}Lockers/{}/'.format(base_url, new_locker.locker_id), data=payload_new,
                           auth=HTTPBasicAuth(db_user, db_pass))
        print 'New locker status change: {}'.format(r_new.status_code)

        payload_old = {
            "locker_rent_confirmed": False,
            "locker_rent_type": None,
            "locker_start_time": None,
            "locker_end_time": None,
            "fk_user": None
        }

        new_headers = {'content-type': 'application/json'}
        r_old = requests.patch('{}Lockers/{}/'.format(base_url, old_locker.locker_id), data=json.dumps(payload_old),
            headers=new_headers, auth=HTTPBasicAuth(db_user, db_pass))
        print 'Old locker status change: {}'.format(r_old.status_code)