__author__ = 'mgradob'
import datetime

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
    def delete_access_level(locker_id=''):
        """
        Returns an XML String for deleting access level to users from SALTO software.
        :return: String.
        """
        return 'STP/00/400/<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?><RequestCall><RequestName> SaltoDBGroup.Update </RequestName><Params><SaltoDBGroup><ExtGroupID> {} </ExtGroupID><SaltoDB.MembershipList.User_Group/></SaltoDBGroup></Params></RequestCall>'.format(locker_id)

    @staticmethod
    def assign_new_key(user_id=''):
        """
        Returns an XML String for to UID card from SALTO software.
        :return: String.
        """
        return 'STP/00/400/<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?><RequestCall><RequestName> Encoder.SaltoDBUser.AssignNewKey </RequestName><Params><ExtUserID> {} </ExtUserID><EncoderID> Encoder#2 </EncoderID></Params></RequestCall>'.format(user_id)

    @staticmethod
    def assign_by_time(locker_id ='0', start_time='00:00:00', end_time='23:59:59',days=['1','1','1','1','1','1','1']):
        """
        Returns an XML String for to UID card from SALTO software.
        :return: String.
        """
        str_assign ='STP/00/600/<?xml version="1.0" encoding="ISO-8859-1"?><RequestCall><RequestName> SaltoDBTimezoneTable.Update </RequestName><Params>' \
                    '<SaltoDBTimezoneTable><TimezoneTableID> {} </TimezoneTableID><SaltoDBTimezoneList><SaltoDBTimezone>' \
                    '<TimezoneID> 1 </TimezoneID><StartTime> {} </StartTime><EndTime> {} </EndTime>' \
                   '<Monday> {} </Monday><Tuesday> {} </Tuesday><Wednesday> {} </Wednesday>' \
                   '<Thursday> {} </Thursday><Friday> {} </Friday><Saturday> {} </Saturday>' \
                   '<Sunday> {} </Sunday></SaltoDBTimezone></SaltoDBTimezoneList></SaltoDBTimezoneTable></Params>' \
                   '</RequestCall>'.format(locker_id,start_time, end_time,
                                           days[0], days[1], days[2], days[3], days[4], days[5], days[6])
        return str_assign

    @staticmethod
    def update_user(id_user=1, locker_id='0', expiration=datetime.datetime.today()):
        """
        str_update = 'STP/00/500/<?xml version="1.0" encoding="ISO-8859-1"?>' \
                     '<RequestCall><RequestName> SaltoDBUser.Update </RequestName>'\
                     '<Params><SaltoDBUser><ExtUserID> {} </ExtUserID>' \
                     '<UserExpiration.Enabled> 1 </UserExpiration.Enabled>' \
                     '<UserExpiration> {} </UserExpiration>' \
                     '</SaltoDBUser></Params></RequestCall>'.format(id_user, expiration)
        """

        str_update = 'STP/00/500/<?xml version="1.0" encoding="ISO-8859-1"?>' \
                     '<RequestCall><RequestName> SaltoDBUser.Update </RequestName>' \
                     '<Params><SaltoDBUser><ExtUserID> {} </ExtUserID>' \
                     '<SaltoDB.AccessPermissionList.User_Door><SaltoDB.AccessPermission.User_Door>' \
                     '<ExtDoorID> {} </ExtDoorID></SaltoDB.AccessPermission.User_Door>' \
                     '</SaltoDB.AccessPermissionList.User_Door>' \
                     '<UserExpiration.Enabled> 1 </UserExpiration.Enabled>' \
                     '<UserExpiration> {} </UserExpiration></SaltoDBUser></Params>' \
                     '</RequestCall>'.format(id_user, locker_id, expiration)

        return str_update

    @staticmethod
    def update_user_two(id_user=1, locker_id='0', locker_id2='0', expiration=datetime.datetime.today()):
        str_update = 'STP/00/600/<?xml version="1.0" encoding="ISO-8859-1"?>' \
                     '<RequestCall><RequestName> SaltoDBUser.Update </RequestName>' \
                     '<Params><SaltoDBUser><ExtUserID> {} </ExtUserID>' \
                     '<SaltoDB.AccessPermissionList.User_Door><SaltoDB.AccessPermission.User_Door>' \
                     '<ExtDoorID> {} </ExtDoorID></SaltoDB.AccessPermission.User_Door>' \
                     '<SaltoDB.AccessPermission.User_Door><ExtDoorID> {} </ExtDoorID>' \
                     '</SaltoDB.AccessPermission.User_Door>' \
                     '</SaltoDB.AccessPermissionList.User_Door>' \
                     '<UserExpiration.Enabled> 1 </UserExpiration.Enabled>' \
                     '<UserExpiration> {} </UserExpiration></SaltoDBUser></Params>' \
                     '</RequestCall>'.format(id_user, locker_id, locker_id2, expiration)

        return str_update

    @staticmethod
    def assign_calendar(locker_id ='0', year=datetime.datetime.today().year, months=[]):
        """
        Returns an XML String for to UID card from SALTO software.
        :return: String.
        """
        return 'STP/00/600/<?xml version="1.0" encoding="ISO-8859-1"?><RequestCall><RequestName> SaltoDBYearCalendar.Update </RequestName><Params><SaltoDBYearCalendar>' \
               '<CalendarID> {} </CalendarID><Year> {} </Year><Month1> {} </Month1><Month2> {}</Month2>' \
               '<Month3> {} </Month3><Month4> {} </Month4><Month5> {} </Month5><Month6> {} </Month6>' \
               '<Month7> {} </Month7><Month8> {} </Month8><Month9> {} </Month9><Month10> {} </Month10>' \
               '<Month11> {} </Month11><Month12> {} </Month12></SaltoDBYearCalendar></Params></RequestCall>'\
                .format(locker_id, year, months)


    @staticmethod
    def update_key(user_id=''):
        """
        Returns an XML String for to UID card from SALTO software.
        :return: String.
        """
        return 'STP/00/400/<?xml version="1.0" encoding="ISO-8859-1"?><RequestCall><RequestName> Encoder.SaltoDBUser.UpdateCurrentKey </RequestName><Params><ExtUserID> {} </ExtUserID><EncoderID> Encoder#2 </EncoderID></Params></RequestCall>'.format(user_id)