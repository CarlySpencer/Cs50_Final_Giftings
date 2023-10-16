from flask import redirect, render_template, session, flash
from functools import wraps 
import mysql.connector

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def connect():
    try:
        cn = mysql.connector.connect(host='localhost', user='root', passwd='abcd', database='gift', auth_plugin='mysql_native_password')
        db = cn.cursor()
        return flash("Database connection successful!")
    except:
        return flash("Cannot connect to database :(")