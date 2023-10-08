from flask import Flask, flash, render_template, redirect, request, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='abcd',
    database='gift'
    )
db = db.cursor()

# create a helpers page with javascript? (instead of flash, error message of some sort, must be logged in function)

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
#if user is visiting page
    if request.method == "GET":
        return render_template("/login")
#if user interacted with form
    else:
        username = request.form.get("username")
        password = request.form.get("password")
#weed out user mischief 
        if not username:
            return flash("Enter username")
        elif not password:
            return flash("Enter password")
#query database for usernames
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
#see if username exists
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], password):
            return flash("Invalid username/password")
#remember logged in user
        session["user_id"] = rows[0]["id"]
        return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
#visiting site
    if request.method == "GET":
        return render_template("/register")
#interacting with form
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        dbusername = db.execute("SELECT * FROM users WHERE username = ?", username)
#weed out user mischief
        if not username:
            return flash("Enter username")
        elif not password:
            return flash("Enter password")
        elif not confirm:
            return flash("Confirm password")
#check if passwords match
        elif password != confirm:
            return flash("Passwords do not match")
#check if username is already in use
        elif len(dbusername) != 0:
            return flash("Username already in use")
#insert new user into database
        hash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, password) VALUES (?, ?)", username, hash)
#remember user 
        session["user_id"] = dbusername[0]["id"]
        return redirect("/")
    

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
def index():
    user_id = session["user_id"]
    people = db.execute("SELECT name, event, date FROM people, events, dates WHERE events.events_id=people.id AND dates.dates_id=event.id AND events.celebrate = '1' AND person.person_id = ?", user_id)
    return render_template("/index.html", people=people)


@app.route("/people", methods=["GET", "POST"])
def people():
    # to complete 
    flash(":)")

@app.route("/add", methods=["GET", "POST"])
def add():
    user_id = session["user_id"]
    if request.method == "GET":
        return render_template("/add")
    else:
        name = request.form.get("name")
        birthday = request.form.get("birthday")
        notes = request.form.get("notes")
        dbname = db.execute("SELECT * FROM people WHERE name = ?", name)
        person_id = db.execute("SELECT id FROM USERS WHERE name = ?", name)

#Check for user mischief 
        if not name:
            flash("Please input a name")
        if len(dbname) != 0:
            flash("Person already has a profile")

#Input name and birthday into people table
        db.execute("INSERT INTO people (name, birthday, notes) VALUES (?, ?, ?) WHERE user = (?)", name, birthday, notes, user_id)

#Input any new events into dates table
        newEvent = request.form.get("addevent")
        newDate = request.form.get("adddate")
        if newEvent != None and newDate != None:
            db.execute("INSERT INTO dates (event, date) VALUES (?, ?)", newEvent, newDate)
        
#Input events into events table
        events = db.execute("SELECT event FROM dates") #If something is wrong its gonna be here 
        for event in events:
            if event != None:
                db.execute("INSERT INTO events (?) VALUES (?) WHERE id = (?)", event, 1, person_id)
            else:
                db.execute("INSERT INTO events (?) VALUES (?) WHERE id = (?)", event, 0, person_id)

    return redirect("/add.html", events=events)


@app.route("/shop", methods=["GET", "POST"])
def shop():
    # to complete
    flash(":)")

@app.route("/interests", methods=["GET", "POST"])
def interests():
    # to complete
    flash(":)")
