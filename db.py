from mysql.connector import connect, Error
import mysql
import scrypt
import rsat


def hashsalt(password):
    salt = b'f55e0fb15c8e93b2bb772be231874962'
    passw = password
    password = bytes(passw, encoding='utf-8')
    key = scrypt.hash(password, salt, 2048, 8, 1, 32)
    return key.hex()

def encrypt(apppass, publicKey):
    encodemessage = rsat.encrypt(apppass.encode(), publicKey)
    return encodemessage

def decrypt(apppass, privateKey):
    decodemessage= rsat.decrypt(apppass, privateKey).decode()
    return decodemessage

class Database():

    def __init__(self):
        self.connect = False
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="tigi",
            password="Zer0shadow",
            database="securestorage"
        )
        self.mycursor = self.mydb.cursor()
        self.id = 0
        self.pubk = ''
        self.privk = ''
        self.exists = False
        self.appname = ''
        self.appuser = ''
        self.apppass = ''
        self.existss = False
    def resetappdetails(self):
        self.appname = ''
        self.appuser = ''
        self.apppass = ''

    def resetk(self):
        self.pubk = ''
        self.privk = ''

    def resetid(self):
        self.id = 0

    def resetexists(self):
        self.exists = False

    def dbconnect(self):

        try:
            mydb = mysql.connector.connect(
                host="localhost",
                user="tigi",
                password="Zer0shadow",
                database="securestorage"
            )
            mycursor = mydb.cursor()

            mycursor.execute("SHOW DATABASES")

            self.connect = True
            for x in mycursor:
                print(x)
        except Error as e:
            print(e)

    def createtables(self):

        if self.connect == True:


            sql1 = """CREATE TABLE IF NOT EXISTS Users (id int PRIMARY KEY AUTO_INCREMENT, username VARCHAR(255), password VARCHAR(255) )"""
            self.mycursor.execute(sql1)
            self.mycursor.execute("SHOW TABLES")
            for x in self.mycursor:
                print(x)

            sql2 = """CREATE TABLE IF NOT EXISTS Passwords (userId int, appname VARCHAR(255), appuser VARCHAR(255), apppass VARBINARY(255))"""
            self.mycursor.execute(sql2)
            self.mycursor.execute("SHOW TABLES")
            for x in self.mycursor:
                print(x)

            sql3 = """CREATE TABLE IF NOT EXISTS encryptKeys (Id int PRIMARY KEY AUTO_INCREMENT, FOREIGN KEY(Id) REFERENCES Users(id), n VARCHAR(255), e VARCHAR(255), d VARCHAR(255), p VARCHAR(255), q VARCHAR(255))"""
            self.mycursor.execute(sql3)
            self.mycursor.execute("SHOW TABLES")
            for x in self.mycursor:
                print(x)
        else:
            print("database not connected")
            exit()
#FOR DEBUG ONLY
    def nuke(self):
        sql3 = """DROP TABLE encryptKeys"""
        self.mycursor.execute(sql3)

        sql2 = """DROP TABLE Passwords"""
        self.mycursor.execute(sql2)

        sql1 = """DROP TABLE Users"""
        self.mycursor.execute(sql1)
#FOR DEBUG ONLY

    def storeuserdetails(self, namee, password):

        hashedpassword = hashsalt(password)
        namee = namee

        sql = """INSERT INTO Users (username, password) VALUES (%s,%s)"""
        val = (namee, hashedpassword)

        self.mycursor.execute(sql, val)

        self.mydb.commit()

        print(self.mycursor.rowcount, "record inserted")

    def checkpassnameexists(self, appname):
        sql1 ="""SELECT * FROM passwords WHERE appname = %(appname)s """
        val = {'appname': appname}
        self.mycursor.execute(sql1, val)
        result = self.mycursor.fetchall()
        if len(result) == 0:
            self.exists = False
            return self.exists
        else:
            self.exists = True

    def checkuserexists(self, user):

        # you need to valid input values as this statement is open for SQL injection c
        #how do i do that?
        sql1 = """SELECT * FROM Users WHERE username = %(username)s"""
        val = {'username' : user}
        self.mycursor.execute(sql1, val)
        # with Select statement you need to check the values returned from the DB 
        # is that what the fetchone() does?
        # Yes its fetching one one matching record
        # where as with update/delete it will probably return boolean or no of records updated
        result = self.mycursor.fetchall()
        #why did you need to result != None?
        #  Just casting value to boolean, as result will hold the matching value from the db
        #oh, i understand now, right
        #if i remove the print statement for print(result), will that get rid of the (1, 'test1', 'dbd9913713bea9587ea9be49dcfaaff19fd356e9b9f6b96856a01fe8b5ad07ea')?
        #  yes
        # (1, 'test1', 'dbd9913713bea9587ea9be49dcfaaff19fd356e9b9f6b96856a01fe8b5ad07ea') !!!!! Security issue
        if len(result) == 0:
            self.exists = False
            return self.exists
        else:
            self.exists = True
            return self.exists

    def getid(self, user, password):
        hashpass= hashsalt(password)
        sql = """SELECT id FROM Users WHERE username = %s AND password = %s"""
        val = (user, hashpass)

        self.mycursor.execute(sql, val)

        result = self.mycursor.fetchall()
        try:
            self.id = result[0][0]
            return self.id
        except:
            self.id = False
            return self.id
    def storeappdetails(self, appname, appuser, apppass):

        userId = self.id
        appname = appname
        appuser = appuser
        apppass = encrypt(apppass, self.pubk)

        sql = """INSERT INTO Passwords (UserId, appname, appuser, apppass) VALUES (%s,%s,%s,%s)"""
        val = (userId, appname, appuser, apppass)

        self.mycursor.execute(sql, val)

        self.mydb.commit()

        print(self.mycursor.rowcount, "record inserted")

    def retrieveappdetails(self, appname, appuser):
        userId = self.id

        sql = """SELECT appname, appuser, apppass FROM Passwords WHERE userId = %(userId)s AND appname = %(appname)s AND appuser = %(appuser)s"""
        val = {'userId': userId,
               'appname': appname,
               'appuser': appuser}
        self.mycursor.execute(sql, val)

        result = self.mycursor.fetchall()


        wantedtup = result[0]
        self.appname = wantedtup[0]
        self.appuser = wantedtup[1]
        self.apppass = decrypt(wantedtup[2], self.privk)
        self.existss=True
        return self.existss

    def givevalapp(self):
        return self.appname, self.appuser, self.apppass


    def storekeyvalues(self):
        publicKey, privateKey = rsat.newkeys(512)
        pvk = privateKey
        n = str(pvk.n)
        e = str(pvk.e)
        d = str(pvk.d)
        p = str(pvk.p)
        q = str(pvk.q)
        sql = """INSERT INTO encryptKeys (n,e,d,p,q) VALUES (%(n)s,%(e)s,%(d)s,%(p)s,%(q)s)"""
        val = {'n': n,
                  'e': e,
                  'd': d,
                  'p': p,
                  'q': q}
        self.mycursor.execute(sql,val)
        self.mydb.commit()
        print(self.mycursor.rowcount, "record inserted")

    def retrievekeyvalues(self):
        UserId = self.id
        sql = """SELECT n, e, d, p, q FROM encryptKeys WHERE Id = %(Id)s"""
        value = {'Id': UserId}
        self.mycursor.execute(sql, value)
        result = self.mycursor.fetchall()
        wantedtup = result[0]
        n = int(wantedtup[0])
        e = int(wantedtup[1])
        d = int(wantedtup[2])
        p = int(wantedtup[3])
        q = int(wantedtup[4])
        self.pubk = rsat.pubformat(n,e)
        self.privk = rsat.privformat(n,e,d,p,q)

db = Database()
db.dbconnect()
db.createtables()
'''
db.checkuserexists('test1')
db.checkuserexists('bruh')
db.storeuserdetails('test1', 'test1')
db.getid('test1','test1')
db.storekeyvalues()
db.retrievekeyvalues()
db.storeappdetails('testapp1', 'testuser1', 'testpass1')
db.retrieveappdetails('testuser1')




db.storekeyvalues()
db.storeuserdetails('test1', 'test1')
db.nuke()
print(db.checkuserdetails('test1', 'test1'))
db.getid('test1','test1')
db.retrievekeyvalues()
db.storeappdetails('testapp1', 'testuser1', 'testpass1')
db.storeappdetails('testapp3','testuser3','testpass3')
db.storeappdetails('testapp4', 'testuser4', 'testpass4')
db.retrieveappdetails('testuser1')
db.rawvalue()
line 57: 19/08/21 v0.1: sql2 = """CREATE TABLE IF NOT EXISTS Passwords (userId int PRIMARY KEY, FOREIGN KEY(userId) REFERENCES Users(id), appname VARCHAR(255), appuser VARCHAR(255), apppass VARCHAR(255))"""'''
