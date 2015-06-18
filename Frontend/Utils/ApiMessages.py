__author__ = 'mgradob'

import json
import requests
import Models
from requests.auth import HTTPBasicAuth
from calendar import monthrange
import datetime

base_url = 'http://localhost:8000/'
"""
headers = {'Content-type': 'application/json', 'Accept': 'text/plain',
           'Pragma': 'no-cache', 'Cache-control': 'no-cache'}
           """
headers = {'content-type': 'application/json',
           'pragma': 'no-cache', 'cache-control': 'no-cache'}

# db_user = 'admin'
# db_pass = 'admin'
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
            data['user_discount'],
            data['user_balance']
        )

    def get_user(self):
        self.get_user_data()
        return self.user

    @staticmethod
    def set_user_balance(user_id, balance=0.0):

        payload = {
            "user_balance": balance
        }

        r = requests.patch('{}Users/{}/'.format(base_url, user_id), data=json.dumps(payload),
                           headers=headers, auth=HTTPBasicAuth(db_user, db_pass))
        print 'New balance: {}'.format(r.status_code)


class Lockers:
    lockers_list = []
    areas_list = []

    def __init__(self, locker=None, rent_confirmation=None):
        if locker is None:
            self.get_lockers()
            self.get_areas()
        else:
            self.confirm_assign_locker(locker, rent_confirmation)

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

    # Return Json from Request of all areas
    @staticmethod
    def get_areas_json():
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
        now_plus_10 = datetime.datetime.today() + datetime.timedelta(minutes=10)
        available = []
        for locker in self.lockers_list:
            locker_area = locker.fk_area.split('Areas/')[1][:-1]
            if locker.fk_user is None and locker_area == str(area_id) and locker.locker_status == "available":
                available.append(locker)
            else:
                print "{}".format(locker.locker_rent_confirmed)
                if not locker.locker_rent_confirmed and locker.locker_start_time is not None:
                    print "XXXX - {}".format(locker.locker_start_time)

                    fmt2 = '%Y-%m-%dT%H:%M:%SZ'
                    x = datetime.datetime.strptime(locker.locker_start_time, fmt2)
                    y = x + datetime.timedelta(minutes=10)
                    print "XXXX - {}".format(y)

                    if now_plus_10 > y:
                        self.make_locker_available(locker.locker_id)
                        available.append(locker)
                        print "FUERA DEL RANGO"
                    else:
                        print "OK"

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

    @staticmethod
    def assign_locker(user_id, locker, rent_type, start_date, end_date):
        # r = requests.delete('{}Lockers/{}'.format(base_url, locker.locker_id), auth=HTTPBasicAuth(db_user, db_pass))
        # print 'Deletion of locker: {}'.format(r.status_code)

        payload = {
            "locker_rent_confirmed": False,
            "locker_rent_type": rent_type,
            "locker_status": "in_use",
            "locker_start_time": start_date,
            "locker_end_time": end_date,
            "fk_user": base_url + "Users/{}/".format(user_id)
        }

        r = requests.patch('{}Lockers/{}/'.format(base_url, locker.locker_id),
                           data=payload, auth=HTTPBasicAuth(db_user, db_pass))

        print 'Locker assignation: {}'.format(r.status_code)

    @staticmethod
    def confirm_assign_locker(locker, rent_confirmation):

        payload = {
            "locker_rent_confirmed": rent_confirmation
        }

        r = requests.patch('{}Lockers/{}/'.format(base_url, locker.locker_id),
                           data=payload, auth=HTTPBasicAuth(db_user, db_pass))
        print 'Locker confirmation: {}'.format(r.status_code)

    @staticmethod
    def change_locker_status(locker_id, locker_status):

        payload = {
            "locker_status": locker_status
        }

        r = requests.patch('{}Lockers/{}/'.format(base_url, locker_id),
                           headers=headers, data=json.dumps(payload), auth=HTTPBasicAuth(db_user, db_pass))
        print 'Locker status change: {}'.format(r.status_code)

    @staticmethod
    def make_locker_available(locker_id):

        payload = {
            "locker_rent_confirmed": False,
            "locker_rent_type": None,
            "locker_status": "available",
            "locker_start_time": None,
            "locker_end_time": None,
            "fk_user": None
        }

        print locker_id
        print json.dumps(payload)
        # headers = {'content-type': 'application/json'}
        r = requests.patch('{}Lockers/{}/'.format(base_url, locker_id), data=json.dumps(payload),
                           headers=headers, auth=HTTPBasicAuth(db_user, db_pass))
        print 'Now Available: {}'.format(r.status_code)

    @staticmethod
    def set_locker_available(locker):

        payload = {
            "locker_rent_confirmed": False,
            "locker_rent_type": None,
            "locker_status": "available",
            "locker_start_time": None,
            "locker_end_time": None,
            "fk_user": None
        }

        r = requests.patch('{}Lockers/{}/'.format(base_url, locker.locker_id),  data=json.dumps(payload),
                          headers=headers, auth=HTTPBasicAuth(db_user, db_pass))
        print 'Now Available: {}'.format(r.status_code)

    @staticmethod
    def locker_paid(locker, user=None, total_pay=None, rent_type=None, end_date=None):
        str_end_time = end_date
        if rent_type == "by_semester":
            str_end_time = locker.locker_end_time

        payload = {
            "log_rent_type": rent_type,
            "log_start_time": locker.locker_start_time,
            "log_end_time": str_end_time,
            "log_time_charged": 0,
            "log_rate": 0,
            "log_discount": 0,
            "log_total_pay": total_pay,
            "log_comments": None,
            "fk_locker_id": '{}Lockers/{}/'.format(base_url, locker.locker_id),
            "fk_user_id": '{}Users/{}/'.format(base_url, user)
        }

        print "DATOS - {}".format(json.dumps(payload))

        # headers = {'content-type': 'application/json'}
        r = requests.post('{}Log/'.format(base_url), data=payload,
                          auth=HTTPBasicAuth(db_user, db_pass))
        print 'Locker PAID Log: {}'.format(r.status_code)

    @staticmethod
    def migrate_locker(old_locker, new_locker):

        payload_new = {
            "locker_rent_confirmed": old_locker.locker_rent_confirmed,
            "locker_rent_type": old_locker.locker_rent_type,
            "locker_status": "in_use",
            "locker_start_time": old_locker.locker_start_time,
            "locker_end_time": old_locker.locker_end_time,
            "fk_user": old_locker.fk_user
        }

        r_new = requests.patch('{}Lockers/{}/'.format(base_url, new_locker.locker_id),
                               data=payload_new, auth=HTTPBasicAuth(db_user, db_pass))
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


class Periods:
    periods_list = []

    def __init__(self):
        self.get_periods()

    def get_periods(self):
        self.periods_list = []
        for period in requests.get(base_url + 'Periods/').json():
            self.periods_list.append(Models.PeriodModel(
                period['period_id'],
                period['period_name'],
                period['period_start_time'],
                period['period_end_time']
            ))

    def get_period(self):
        return self.periods_list


class Rates:
    rates_list = []

    def __init__(self):
        self.get_rate_list()

    def get_rate_list(self):
        self.rates_list = []
        for rate in requests.get(base_url + 'Rates/').json():
            self.rates_list.append(Models.RateModel(
                rate['rate_id'],
                rate['rate_name'],
                rate['rate_rate'],
                rate['rate_unit'],
                rate['rate_currency']
            ))

    def get_rates(self):
        return self.rates_list


class Log:
    user = None
    log_list = []

    def __init__(self, user=None):
        self.user = user

    def get_log(self, month):
        self.log_list = []
        days_of_month = monthrange(2015, int(month))
        current_year = datetime.datetime.now().year
        print "{} - {}".format(current_year, days_of_month)

        req = requests.get('{}Log_Search/?user={}&min_date_start={}-{}-01%2000:00:00&max_date_start={}-{}-28%2023:59:59'
                           .format(base_url,self.user, current_year, month, current_year, month),
                           auth=HTTPBasicAuth(db_user, db_pass)).json()
        return req