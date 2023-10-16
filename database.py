import mysql.connector

def createDatabase():
    cn = mysql.connector.connect(host='localhost', user='root', passwd='abcd', database='gift', auth_plugin='mysql_native_password')
    db = cn.cursor()
    db.execute("CREATE DATABASE IF NOT EXISTS giftings")
    db.execute("")
    db.close()
    cn.close()

def createTables():
    cn = mysql.connector.connect(host='localhost', user='root', passwd='abcd', database='gift', auth_plugin='mysql_native_password')
    db = cn.cursor()
    db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER AUTO_INCREMENT NOT NULL PRIMARY KEY, username TEXT, password TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS people (id INTEGER AUTO_INCREMENT NOT NULL PRIMARY KEY, person_id INTEGER, FOREIGN KEY (person_id) REFERENCES users(id), name TEXT, birthday TEXT, notes TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER AUTO_INCREMENT NOT NULL PRIMARY KEY, events_id INTEGER, uevents_id INTEGER, FOREIGN KEY (events_id) REFERENCES people(id), FOREIGN KEY (uevents_id) REFERENCES users(id), event TEXT, date TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS interests (id INTEGER AUTO_INCREMENT NOT NULL PRIMARY KEY, interests_id INTEGER, uinterests_id INTEGER, FOREIGN KEY (interests_id) REFERENCES people(id), FOREIGN KEY (uinterests_id) REFERENCES users(id), interests TEXT)")
    db.close()
    cn.close()

