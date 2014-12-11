import datetime
import simplejson as json
from requests.auth import HTTPBasicAuth
from Frontend.Utils import Models

__author__ = 'mgradob'

import requests

# r = requests.get('http://localhost:8000/Users/a01560157')
# print r.status_code
# print r.text
# print r.json()['user_id']
# print r.json()['user_name']
# print r.json()['user_ap']
# print r.json()['user_am']
# print r.json()['user_matricula']
# print r.json()['user_discount']
#
# r = requests.get('http://localhost:8000/Areas/0')
# print r.status_code
# print r.text
# print r.json()['area_id']
# print r.json()['area_name']
# print r.json()['area_description']
# print r.json()['area_enable']

# r = requests.get('http://localhost:8000/Lockers/')
# print 'Status code'
# print r.status_code
# print 'Text'
# print r.text
# print 'Details'
# print r.json()[0]['fk_user']
# print r.json()[1]

# for locker in requests.get('http://localhost:8000/Lockers/').json():
#     if locker['fk_user'] is None:
#         pass
#     else:
#         print 'Locker: {}'.format(locker['fk_user'].split('Users/')[1][:-1])

base_url = 'http://localhost:8000/'

# class Lockers:
#     lockers_list = []
#     areas_list = []
#
#     def __init__(self):
#         self.get_lockers()
#         self.get_areas()
#
#     def get_lockers(self):
#         for locker in requests.get('http://localhost:8000/Lockers/').json():
#             self.lockers_list.append(Models.LockerModel(
#                 locker['locker_id'],
#                 locker['locker_name'],
#                 locker['locker_match'],
#                 locker['locker_status'],
#                 locker['locker_start_time'],
#                 locker['fk_area'],
#                 locker['fk_user']
#             ))
#
#         # for locker in self.lockers_list:
#         #     r = requests.get(locker.fk_area).json()
#         #     if self.areas_list.count(r['area_name']) is 0:
#         #         self.areas_list.append(r['area_name'])
#
#     def get_areas(self):
#         for area in requests.get('http://localhost:8000/Areas/').json():
#             self.areas_list.append(Models.AreaModel(
#                 area['area_id'],
#                 area['area_name'],
#                 area['area_description'],
#                 area['area_enable']
#             ))
#
#     def get_available_lockers(self):
#         available = []
#         for locker in self.lockers_list:
#             if locker.fk_user is None:
#                 available.append(locker)
#         return available
#
#     def has_assigned_locker(self, user):
#         for locker in self.lockers_list:
#             if locker.fk_user is not None:
#                 if user == locker.fk_user.split('Users/')[1][:-1]:
#                     return True
#         return False
#
# lockers = Lockers()
# print 'All lockers'
# for locker in lockers.lockers_list:
#     print locker.locker_id
# print 'Available lockers'
# av = lockers.get_available_lockers()
# for lk in av:
#     print lk.locker_id
# print 'Getting areas'
# print len(lockers.areas_list)
# for area in lockers.areas_list:
#     print area.area_name
#
# area_p = 'in_prep'
# print 'Finding area ' + area_p
# for area in lockers.areas_list:
#     if area.area_name == area_p:
#         print area.area_id
#     else:
#         print None
#
# r = requests.delete('{}Lockers/{}'.format(base_url, 1), auth=HTTPBasicAuth('admin', 'admin'))
#
# print 'Date: ' + str(datetime.datetime(2014, 12, 4, 23, 59, 59))

# r = requests.get(base_url + 'Lockers/1')
# print r.json()
#
#
# response = json.dumps({
#     'locker_id': 1,
#     'locker_name': 'A1',
#     'locker_match': 'False',
#     'locker_status': 'En Uso',
#     'locker_start_time': None,
#     'fk_area': 'http://localhost:8000/Areas/0/',
#     'fk_user': 'http://localhost:8000/Users/CD2EE4DD/'
# })
#
# print 'Response: ' + response
#
# p = requests.put(base_url + 'Lockers/1', response, auth=HTTPBasicAuth('admin', 'admin'))
# print p.text

from datetime import datetime
import time

fmt = '%Y-%m-%d %H:%M:%S'
d1 = datetime.strptime(datetime.now().strftime(fmt), fmt)
d2 = datetime.strptime('2014-12-20 00:00:00', fmt)

# convert to unix timestamp
d1_ts = time.mktime(d1.timetuple())
d2_ts = time.mktime(d2.timetuple())

# they are now in seconds, subtract and then divide by 60 to get minutes.
minutes_to_pay = int(d2_ts-d1_ts) / 60

total = minutes_to_pay * 0.05
print '%.2f' % int(total)