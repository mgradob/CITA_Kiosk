__author__ = 'mgradob'


class UserModel:
    user_id = None
    user_name = None
    user_ap = None
    user_am = None
    user_discount = None
    user_mat = None

    def __init__(self, id_user=None, name=None, ap=None, am=None, discount=None, matricula=None):
        self.user_id = id_user
        self.user_name = name
        self.user_ap = ap
        self.user_am = am
        self.user_discount = discount
        self.user_mat = matricula