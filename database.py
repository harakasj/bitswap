from time import gmtime, strftime

import pymysql


def tstamp():
    return strftime("%H:%M:%S", gmtime())

class Database():
    sys_user = "sommerville"
    sys_pwd = "ian_sommerville_is_a_little_bitch"
    schema = "dbchat"
    addr = "192.168.1.3"
    user_t = "users"
    is_connected = False
    
    def connect(self):
        try:
            self.db = pymysql.connect(self.addr,self.sys_user,self.sys_pwd,self.schema )
            self.is_connected = True
            self.cursor = self.db.cursor()
            print("%s [DATABASE]: Connecting." % ( tstamp()))
            
        except pymysql.Error:
            print("Error connecting to database!")
            print("User: %s \nAddress: %s" %(self.sys_user, self.addr))
            self.is_connected = False 
        print("%s [DATABASE]: Connected." % ( tstamp() ) )
        return
    
    def destroy(self):
        self.db.close()
        return True
    
    def query(self,cmd):
        try:
            self.cursor.execute(cmd)
            data = self.cursor.fetchall()
            print(data)
        except pymysql.Error as e:
            print(e)
            pass
        
    def query_contact(self,user):
        
        q = ("select contact, `group` from (" 
             "%(0)s.contact join %(0)s.users  on username = users_contact )"
             " where username = '%(1)s';" % {"0":self.schema,"1":user} )
        print(q)
        print("%s [DATABASE]: Querying contacts for %s." % ( tstamp(),user ) )
        try:
            self.cursor.execute(q)
            data = self.cursor.fetchall()
            return (data)
        except pymysql.Error as e:
            print(e)
            pass
        
    def add_user(self,user,pwd):
        if ( self.is_connected ):
            insert = ("INSERT INTO `chatdb`.`users` (`username`,`password`) VALUES ('%s','%s','%s', 10009);") % (user,"none",pwd)
            self.cursor.execute(insert)
            
    def check_login(self,user,pwd):
        if ( self.is_connected ):
            check = ("SELECT username,password  FROM %(0)s"
                     " WHERE username = '%(1)s';"
                    % {"0":self.user_t, "1":user,"2":pwd } )
            self.cursor.execute(check)
            data = self.cursor.fetchall()
            if ( len(data) > 0 ): 
                if user in data[0][0]:
                    
                    print("%s [DATABASE]: %s found." % ( tstamp(), user ) )
                    print(data[0])
                    if pwd == data[0][1]:
                        print("%s [DATABASE]: password correct." % ( tstamp() ) )
                        print("%s [DATABASE]: %s authenticated." % ( tstamp(), user ) )
                        return True
                    else:
#                         print("Password: INCORRECT")
                        print("%s [DATABASE]: password incorrect" % ( tstamp() ) )
                        return False
                return False
            else: 
                print("%s [DATABASE]: %s not found." % ( tstamp(), user ) )
                return False 
        else:
            self.connect()
        return False

def testrun():
    db = Database()
    db.connect()
#     db.check_login("skankhunt42", "notgonnabother")
#     db.add_user("abc22223", "123")

#     db.check_login("john", "123")
#     db.query_contact("john")
#     db.destroy()
    return
     
    
# testrun()