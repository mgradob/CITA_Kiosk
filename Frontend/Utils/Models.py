__author__ = 'mgradob'


class UserModel:
    user_id = None
    user_name = None
    user_ap = None
    user_am = None
    user_discount = None
    user_mat = None

    def __init__(self, id_user=None, name=None, ap=None, am=None, matricula=None, discount=None) :
        self.user_id = id_user
        self.user_name = name
        self.user_ap = ap
        self.user_am = am
        self.user_discount = discount
        self.user_mat = matricula


class LockerModel:
    locker_id = None
    locker_name = None
    locker_rent_confirmed = None
    locker_rent_type = None
    locker_status = None
    locker_start_time = None
    locker_end_time = None
    fk_area = None
    fk_user = None

    def __init__(self, id_locker=None, name=None, rent_confirmed=None, rent_type=None, status=None,
                 start_time=None, end_time=None, area=None, user=None):
        self.locker_id = id_locker
        self.locker_name = name
        self.locker_rent_confirmed = rent_confirmed
        self.locker_rent_type = rent_type
        self.locker_status = status
        self.locker_start_time = start_time
        self.locker_end_time = end_time
        self.fk_area = area
        self.fk_user = user


class AreaModel:
    area_id = None
    area_name = None
    area_description = None
    area_enable = None

    def __init__(self, id_area=None, name=None, desc=None, enable=None):
        self.area_id = id_area
        self.area_name = name
        self.area_description = desc
        self.area_enable = enable