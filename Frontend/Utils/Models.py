__author__ = 'mgradob'


class UserModel:
    user_id = None
    user_name = None
    user_ap = None
    user_am = None
    user_discount = None
    user_mat = None
    user_balance = None

    def __init__(self, id_user=None, name=None, ap=None, am=None, matricula=None, discount=None, balance=0.0) :
        self.user_id = id_user
        self.user_name = name
        self.user_ap = ap
        self.user_am = am
        self.user_discount = discount
        self.user_mat = matricula
        self.user_balance = balance


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


class PeriodModel:
    period_id = None
    period_name = None
    period_start_time = None
    period_end_time = None

    def __init__(self, period_id=None, name=None, start_time=None, end_time=None):
        self.period_id = period_id
        self.period_name = name
        self.period_start_time = start_time
        self.period_end_time = end_time


class RateModel:
    rate_id = None
    rate_name = None
    rate_rate = None
    rate_unit = None
    rate_currency = None

    def __init__(self, rate_id=None, rate_name=None, rate_rate=None, rate_unit=None, rate_currency=None):
        self.rate_id = rate_id
        self.rate_name = rate_name
        self.rate_rate = rate_rate
        self.rate_unit = rate_unit
        self.rate_currency = rate_currency


class LogModel:
    log_id=None
    log_timestamp = None
    log_start_time = None
    log_end_time = None
    log_time_charged = None
    log_rent_type = None
    log_rate = None
    log_discount = None
    log_total_pay = None
    log_comments = None
    fk_locker_id = None
    fk_user_id = None

    def __init__(self, log_id=None, log_timestamp = None, log_start_time = None, log_end_time = None,
                 log_time_charged = None, log_rent_type = None, log_rate = None, log_discount = None,
                 log_total_pay = None, log_comments = None, fk_locker_id = None, fk_user_id = None):
        self.log_id = log_id
        self.log_timestamp = log_timestamp
        self.log_start_time = log_start_time
        self.log_end_time = log_end_time
        self.log_time_charged = log_time_charged
        self.log_rent_type = log_rent_type
        self.log_rate = log_rate
        self.log_discount = log_discount
        self.log_total_pay = log_total_pay
        self.log_comments = log_comments
        self.fk_locker_id = fk_locker_id
        self.fk_user_id = fk_user_id