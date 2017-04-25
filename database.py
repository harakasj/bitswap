import time

import pymysql

# Insert = "'INSERT INTO `%s`.`%s` (`contact`,`users_contact`) VALUES ('%s','%s');"
#
Group = "'INSERT INTO `%s`.`%s` (`contact`,`group`,`users_contact`) VALUES ('%s','%s','%s');"

# Insert = "'INSERT INTO `%s`.`%s` (`contact`,`group`,`users_contact`) VALUES (%s,%s,%s);"

def tstamp():
    return time.strftime("%H:%M:%S", time.gmtime())

# TODO
"""
Complete list of all queries needed
Make database credentials protected variables 
    create new users
    add users to contacts
    remove users from contacts
    create new groups
    add users to groups
    remove users from groups
    modify groups names
    modify group contacts
"""


class Database(object):
    sys_user = ""
    sys_pwd = ""
    schema = "test2"
    addr = "192.168.1.3"
    user_t =  "users"
    is_connected = False

    def connect(self):
        try:
            self.db = pymysql.connect(self.addr, self.sys_user, self.sys_pwd, self.schema)
            self.is_connected = True
            self.cursor = self.db.cursor()
            print("%s [DATABASE]: Connecting." % (tstamp()))

        except pymysql.Error:
            print("Error connecting to database!")
            print("User: %s \nAddress: %s" % (self.sys_user, self.addr))
            self.is_connected = False
        print("%s [DATABASE]: Connected." % (tstamp()))
        return

    @property
    def destroy(self):
        self.db.close()
        return True

    # A generic query method, doesn't really do anything right now.
    # TODO
    def query(self, cmd):
        try:
            self.cursor.execute(cmd)
            data = self.cursor.fetchall()
            print(data)
        except pymysql.Error as e:
            print(e)
            pass

    def query_contact(self, user):
        """
        :param user: 
        :return: list tuple
        Called by: Server.handle_request()
        
        Query contacts for a user and a group they are in (if any) and returns list tuple of (contact, group)
        """
        q = ("select contact, `cgroup` from ("
             "%(0)s.contacts join %(0)s.users  on username = cuser )"
             " where username = '%(1)s';" % {"0": self.schema, "1": user})
        # print(q)
        print("%s [DATABASE]: Querying contacts for %s." % (tstamp(), user))
        try:
            self.cursor.execute(q)
            data = self.cursor.fetchall()
            return data
        except pymysql.Error as e:
            print(e)
            return None

    def add_user(self, user, pwd):
        # TODO
        """
        :param user: 
        :param pwd: 
        Called by: Server
        
        Add a new user, fix me and my commands.
        """
        if self.is_connected:
            insert = "INSERT INTO `chatdb`.`users` (`username`,`password`) VALUES ('%s','%s','%s');" \
                     % (user, "none", pwd)
            self.cursor.execute(insert)

    def check_login(self, user, pwd):
        """
        :param user: 
        :param pwd: 
        :return: 
        Called by : Server.handle_login()
        
        queries the login credentials of a user and password.
        Returns true if both username and password is found in the database. Otherwise return false
        """
        if self.is_connected:
            check = ("SELECT username,password  FROM %(0)s"
                     " WHERE username = '%(1)s';" % {"0": self.user_t, "1": user, "2": pwd})
            self.cursor.execute(check)
            data = self.cursor.fetchall()
            if len(data) > 0:
                if user in data[0][0]:

                    print("%s [DATABASE]: %s found." % (tstamp(), user))
                    print(data[0])
                    if pwd == data[0][1]:
                        print("%s [DATABASE]: password correct." % (tstamp()))
                        print("%s [DATABASE]: %s authenticated." % (tstamp(), user))
                        return True
                    else:
                        print("%s [DATABASE]: password incorrect" % (tstamp()))
                        return False
                return False
            else:
                print("%s [DATABASE]: %s not found." % (tstamp(), user))
                return False
        else:
            self.connect()
        return False


def testrun():
    # Just for testing/debugging.
    db = Database()
    db.connect()
    db.check_login("john", "111")
    db.destroy
    return

    # Uncomment this if you wanna run some tests
    # testrun()

# Insert = "INSERT INTO `test2`.`contacts` (`cuser`,`contact`,`cgroup`) VALUES ('%s','%s','%s');"
#
# Delete = "DELETE FROM `test2`.`contacts` WHERE `cuser`='%s' and contact='%s';"
#
# Update = "UPDATE `test2`.`contacts` SET `cgroup` = '%s' WHERE contact='%s' and cgroup='%s';"
#
#
# Login = namedtuple("Login", "action user pwd")
# Request = namedtuple("Request", "action user contact group")
# Message = namedtuple("Message", "tstamp sender recv msg")
# Status = namedtuple("Status", "user status")
#
# user_login = Login(action='logon', user='john', pwd='Password123')
# user_logoff = Login(action='logoff', user='john', pwd=None)
#
# user_status = Status(user='john', status='online')
# user_msg = Message(tstamp=tstamp(), sender='john', recv='joe', msg='Hey how are you doing today?')
#
# contact_add = Request(action='Delete', user='john', contact='joe', group=None)
# contact_del = Request(action='Delete', user='john', contact='joe', group=None)
#
# group_add = Request(action='Add', user='john', contact=None, group='friends')
# group_del = Request(action='Delete', user='john', contact=None, group='friends')
# contact_group_del = Request(action='Delete', user='john', contact='joe', group='friends')
#
#
#
#
# # print(Insert)
# # print(Insert % ('a','b','c','d'))
# r  = Request('Add',"'john'",None,"'friends'")
# # user_add = Request('Add','john'","'joe'","'friends'")
# # user_del = Request('Delete',"'john'","'joe'","'friends'")
# # group_del =Request('Delete',"'john'","'joe'","'friends'")
# # print(Insert % (r.user, r.contact, ("NULL" if r.group is None else r.group)))
#
#
# print(Insert % (r.user,("NULL" if r.contact is None else r.contact), ("NULL" if r.group is None else r.group)))
#
# print(Insert % (r.user,("NULL" if r.contact is None else r.contact), ("NULL" if r.group is None else r.group)))
