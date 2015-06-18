__author__ = 'mgradob'

import threading
from Frontend.Utils import Models

class DataHolder(threading.Thread):
    user_locker = Models.LockerModel
    card_key = ''
    total = 0
    balance = 0
    area_name = ''
    area_id = ''
    total_hours = 0
    end_date = None
    rate_h = None
    rate_d = None
    rate_w = None
    rate_s = None
    rent_type = None
    user = None

    def __init__(self):
        super(DataHolder, self).__init__()

    def run(self):
        print 'DataHolder running'