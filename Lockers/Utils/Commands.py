__author__ = 'mgradob'


class Commands:
    """
    Commands Class.
     Defines all commands used by the Lockers Thread.
    """

    def __init__(self):
        pass

    @staticmethod
    def open_locker(door_id='Lector Mural'):
        """
        Returns an XML String for opening locker doors.
        :return: String.
        """
        return 'STP/00/196/<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?><RequestCall><RequestName>OnlineDoor.Open</RequestName><Params><DoorNameList><DoorID>{}</DoorID></DoorNameList></Params></RequestCall>'.format(door_id)

    @staticmethod
    def read_key(encoder_id='Encoder#2', return_rom_code=1, return_locker_data=1):
        """
        Returns an XML String for reading RFID cards.
        :return: String.
        """
        return 'STP/00/248/<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?><RequestCall><RequestName> Encoder.ReadKey </RequestName><Params><EncoderID> {} </EncoderID><ReturnROMCode> {} </ReturnROMCode><ReturnLockerData> {} </ReturnLockerData></Params></RequestCall>'.format(encoder_id, return_rom_code, return_locker_data)

    @staticmethod
    def read_user(max_count=1):
        """
        Returns an XML String for reading user information from SALTO software.
        :return: String.
        """
        return 'STP/00/100/<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?><RequestCall><RequestName> SaltoDBUserList.Read </RequestName><Params><MaxCount> {} </MaxCount></Params></RequestCall>'.format(max_count)

    @staticmethod
    def update_user(ext_user_id='TestUser', user_expiration_enable=1, user_expiration='2014-06-30T12:30:00'):
        """
        Returns an XML String for updating user information from SALTO software.
        :return: String.
        """
        return 'STP/00/500/<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?><RequestCall><RequestName> SaltoDBUser.Update </RequestName><Params><SaltoDBUser><ExtUserID> {} </ExtUserID><UserExpiration.Enabled> {} </UserExpiration.Enabled><UserExpiration> {} </UserExpiration></SaltoDBUser></Params></RequestCall>'.format(ext_user_id, user_expiration_enable, user_expiration)

    @staticmethod
    def assign_access_level(locker_id='', user_id=''):
        """
        Returns an XML String for assigning access level to users from SALTO software.
        :return: String.
        """
        return 'STP/00/400/<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?><RequestCall><RequestName> SaltoDBGroup.Update </RequestName><Params><SaltoDBGroup><ExtGroupID> {} </ExtGroupID><SaltoDB.MembershipList.User_Group><SaltoDB.Membership.User_Group><ExtUserID> {} </ExtUserID></SaltoDB.Membership.User_Group></SaltoDB.MembershipList.User_Group></SaltoDBGroup></Params></RequestCall>'.format(locker_id, user_id)

    @staticmethod
    def assign_new_key(user_id=''):
        """
        Returns an XML String for to UID card from SALTO software.
        :return: String.
        """
        return 'STP/00/400/<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?><RequestCall><RequestName> Encoder.SaltoDBUser.AssignNewKey </RequestName><Params><ExtUserID> {} </ExtUserID><EncoderID> Encoder#2 </EncoderID></Params></RequestCall>'.format(user_id)

    @staticmethod
    def assign_by_time(user_id=''):
        """
        Returns an XML String for to UID card from SALTO software.
        :return: String.
        """
        return 'STP/00/400/<?xml version="1.0" encoding="ISO-8859-1"?><RequestCall><RequestName> SaltoDBTimezoneTable.Update </RequestName><Params><SaltoDBTimezoneTable><TimezoneTableID> 2 </TimezoneTableID><SaltoDBTimezoneList><SaltoDBTimezone><TimezoneID> 1 </TimezoneID><StartTime> 8:00:00 </StartTime><EndTime> 12:30:00 </EndTime><Monday>1</Monday></SaltoDBTimezone></SaltoDBTimezoneList></SaltoDBTimezoneTable></Params></RequestCall>'


    @staticmethod
    def assign_by_time2(user_id=''):
        """
        Returns an XML String for to UID card from SALTO software.
        :return: String.
        """
        return 'STP/00/400/<?xml version="1.0" encoding="ISO-8859-1"?><RequestCall><RequestName> SaltoDBYearCalendar.Update </RequestName><Params><SaltoDBYearCalendar><CalendarID> 2 </CalendarID><Year> 2015 </Year><Month1>1111111111111111111111111111111</Month1><Month2>1111111111111111111111111111111</Month2><Month3>1111111111111111111111111111111</Month3><Month4>1111111111111111111111111111111</Month4><Month5>1111111111111111111111111111111</Month5><Month6>1111111111111111111111111111111</Month6><Month7>1111111111111111111111111111111</Month7><Month8>1111111111111111111111111111111</Month8><Month9>1111111111111111111111111111111</Month9><Month10>1111111101111111111111111111111</Month10><Month11>1111111111111111111111111111111</Month11><Month12>1111111111111111111111111111111</Month12></SaltoDBYearCalendar></Params></RequestCall>'


    @staticmethod
    def update_key(user_id=''):
        """
        Returns an XML String for to UID card from SALTO software.
        :return: String.
        """
        return 'STP/00/400/<?xml version="1.0" encoding="ISO-8859-1"?><RequestCall><RequestName> Encoder.SaltoDBUser.UpdateCurrentKey </RequestName><Params><ExtUserID> {} </ExtUserID><EncoderID> Encoder#2 </EncoderID></Params></RequestCall>'.format(user_id)