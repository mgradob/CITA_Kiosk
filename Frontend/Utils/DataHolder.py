__author__ = 'mgradob'

import threading
from Frontend.Utils import Models


class DataHolder(threading.Thread):
    user_locker = Models.LockerModel
    card_key = ''
    total = 0
    area_name = ''
    area_id = ''

    def __init__(self):
        super(DataHolder, self).__init__()

    def run(self):
        print 'DataHolder running'