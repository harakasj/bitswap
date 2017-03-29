import time
import pymysql

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


class Database():
    sys_user = ""
    sys_pwd = ""
    schema = "dbchat"
    # addr = ""
    user_t = "users"
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
        q = ("select contact, `group` from ("
             "%(0)s.contact join %(0)s.users  on username = users_contact )"
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
