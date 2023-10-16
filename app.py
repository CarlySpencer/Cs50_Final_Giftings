from flask import Flask, flash, render_template, redirect, request, session
from flask_session import Session
from passlib.hash import sha256_crypt
import mysql.connector
from helpers import login_required, connect
import database


app = Flask(__name__, template_folder='templates')
app.secret_key = '12345'

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


database.createDatabase()
database.createTables()



@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
#if user requested form
    if request.method == "GET":
        return render_template("login.html")
    
#if user interacted with form
    else:
        connect()

#get variables from form
        username = request.form.get("username")
        password = request.form.get("password")

#weed out user mischief 
        if not username:
            flash("Enter username")
            return render_template("login.html")
        elif not password:
            flash("Enter password")
            return render_template("login.html")

#connect to database
        cn = mysql.connector.connect(host='localhost', user='root', passwd='abcd', database='gift', auth_plugin='mysql_native_password')
        db = cn.cursor(buffered=True)

#see if username exists
        db.execute("SELECT username FROM users WHERE username = %s", [username])
        user = db.fetchone()
        if user is None:
            flash("Invalid username")
            return render_template("login.html")

#check if passwords match
        db.execute("SELECT password FROM users WHERE username = %s", [username])
        data = db.fetchone()
        hash = data[0]
        if sha256_crypt.verify(password, hash):
            db.execute("SELECT id FROM users WHERE username = %s", [username])
            id = db.fetchone()
            session['user_id'] = id
            session['logged_in'] = True
            session['username'] = username
        else:
            flash("Invalid password")
            return render_template("login.html")

#disconnect from database
        cn.close()
        db.close()
        return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
#interacting with form
    if request.method == "POST":
        cn = mysql.connector.connect(host='localhost', user='root', passwd='abcd', database='gift', auth_plugin='mysql_native_password')
        db = cn.cursor(buffered=True)
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        dbusername = db.execute("SELECT * FROM users WHERE username = %s", [username])

#weed out user mischief
        if not username:
            flash("Enter username")
            return render_template("register.html")
        elif not password:
            flash("Enter password")
            return render_template("register.html")
        elif not confirm:
            flash("Confirm password")
            return render_template("register.html")

#check if passwords match
        elif password != confirm:
            flash("Passwords do not match")
            return render_template("register.html")

#check if username is already in use
        elif dbusername:
            flash("Username already in use")
            return render_template("register.html")

#insert new user into database
        hash = sha256_crypt.hash(password)
        db.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hash))
        cn.commit()
        cn.close()
        db.close()
        return redirect("/login")

#if visiting page 
    else:
        return render_template("register.html")



@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")



@app.route("/", methods=["GET", "POST"])
@login_required
def index():
#connect to database
    cn = mysql.connector.connect(host='localhost', user='root', passwd='abcd', database='gift', auth_plugin='mysql_native_password')
    db = cn.cursor(buffered=True)

#get birthday display info
    db.execute("SELECT id FROM users WHERE id = %s", session['user_id'])
    userid = db.fetchone()[0]
    db.execute("SELECT name, birthday, notes FROM people WHERE person_id = %s ORDER BY birthday ASC", [userid])
    birthdays = db.fetchall()

#get person info for select menu
    db.execute("SELECT id FROM users WHERE id = %s", session['user_id'])
    userid = db.fetchone()[0]
    db.execute("SELECT name FROM people WHERE person_id = %s", [userid])
    people = db.fetchall()

    if request.method == "POST":
#get form/ db info
        name = request.form.get("person")
        if not name:
            flash("Select a person to see thier information")
            return redirect("/")
        db.execute("SELECT id FROM people WHERE name = %s", [name])
        personid = db.fetchone()[0]
        db.execute("SELECT event, date FROM events WHERE uevents_id = %s AND events_id = %s ORDER BY date", (userid, personid))
        events = db.fetchall()
        db.execute("SELECT interests FROM interests WHERE uinterests_id = %s AND interests_id = %s", (userid, personid))
        interests = db.fetchall()
        return render_template("index.html", name=name, events=events, interests=interests, birthdays=birthdays, people=people, index=True)
#close database
    db.close()
    cn.close()
    return render_template("index.html", birthdays=birthdays, people=people)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
#connect to database
    cn = mysql.connector.connect(host='localhost', user='root', passwd='abcd', database='gift', auth_plugin='mysql_native_password')
    db = cn.cursor(buffered=True)
#get info for table
    db.execute("SELECT id FROM users WHERE id = %s", session['user_id'])
    userid = db.fetchone()[0]
    db.execute("SELECT name, birthday, notes FROM people WHERE person_id = %s", [userid])
    people = db.fetchall()

    if request.method == "POST":

#get form and database info
        name = request.form.get("name")
        birthday = request.form.get("birthday")
        notes = request.form.get("notes")
        db.execute("SELECT * FROM people WHERE name = %s", [name])
        dbname = db.fetchone()

#check for user mischief 
        if not name:
            flash("Please input a name")
            return render_template("add.html")
        if dbname:
            flash("Person already has a profile")
            return render_template("add.html")

#input name and birthday into people table
        db.execute("INSERT INTO people (person_id, name, birthday, notes) VALUES (%s, %s, %s, %s)", (userid, name, birthday, notes))
        cn.commit()
        flash("Person successfully registered!")
        return redirect("/add")

#close database
    cn.close()
    db.close()
    return render_template("add.html", people=people)



@app.route("/editPerson", methods=["GET", "POST"])
@login_required
def edit_person():
#connect to database
    cn = mysql.connector.connect(host='localhost', user='root', passwd='abcd', database='gift', auth_plugin='mysql_native_password')
    db = cn.cursor(buffered=True)

#get info for select menu
    db.execute("SELECT id FROM users WHERE id = %s", session['user_id'])
    userid = db.fetchone()[0]
    db.execute("SELECT name FROM people WHERE person_id = %s", [userid])
    people = db.fetchall()

    if request.method == "POST":
#get form info
        name = request.form.get("newName")
        birthday = request.form.get("newBirth")
        notes = request.form.get("newNotes")
        person = request.form.get("person")

        if not person:
            flash("Please select whose information you would like to edit")
            return render_template("add.html")
        if name:
            db.execute("UPDATE people SET name = %s WHERE name = %s AND person_id = %s", (name, person, userid))
            cn.commit()
        elif birthday:
            db.execute("UPDATE people SET birthday = %s WHERE name = %s AND person_id = %s", (birthday, person, userid))
            cn.commit()
        elif notes:
            db.execute("UPDATE people SET notes = %s WHERE name = %s AND person_id = %s", (notes, person, userid))
            cn.commit()
        flash("Changes successful")
        return redirect("/add")

#close database
    db.close()
    cn.close()
    return render_template("add.html", people=people)


@app.route("/events", methods=["GET", "POST"])
@login_required
def add_event():
#connect to database
    cn = mysql.connector.connect(host='localhost', user='root', passwd='abcd', database='gift', auth_plugin='mysql_native_password')
    db = cn.cursor(buffered=True)

#get person info for select menu
    db.execute("SELECT id FROM users WHERE id = %s", session['user_id'])
    userid = db.fetchone()[0]
    db.execute("SELECT name FROM people WHERE person_id = %s", [userid])
    people = db.fetchall()

#get database info for log table
    db.execute("SELECT events.event, events.date, people.name FROM events JOIN people ON events.events_id=people.id WHERE people.person_id = %s ORDER BY people.name", [userid])
    logged = db.fetchall()

#if interacting with form
    if request.method == "POST":

#get form info
        person = request.form.get("person")
        newEvent = request.form.get("addevent")
        newDate = request.form.get("adddate")

#check for user mischief
        if not newEvent or not newDate or not person:
            flash("Fill out all fields")
            return redirect("/events")
#insert new event into events table
        else:
            db.execute("SELECT * FROM people WHERE name = %s", [person])
            id = db.fetchone()[0]
            db.execute("INSERT INTO events (events_id, uevents_id, event, date) VALUES (%s, %s, %s, %s)", (id, userid, newEvent, newDate))
            cn.commit()
            flash("Event successfully added")
            return redirect("/events")
#close database
    db.close()
    cn.close()
    return render_template("events.html", people=people, logged=logged)



@app.route("/deleteEvent", methods=["GET", "POST"])
@login_required
def delete_event():
#connect to database
    cn = mysql.connector.connect(host='localhost', user='root', passwd='abcd', database='gift', auth_plugin='mysql_native_password')
    db = cn.cursor(buffered=True)

    if request.method == "POST":
#get form data
        person = request.form.get("name")
        event = request.form.get("event")
        db.execute("SELECT id FROM users WHERE id = %s", session['user_id'])
        userid = db.fetchone()[0]
        db.execute("SELECT id FROM people WHERE name = %s AND person_id = %s", (person, userid))
        personid = db.fetchone()[0]
    
#delete event
        db.execute("DELETE FROM events WHERE events_id = %s AND uevents_id = %s AND event = %s", (personid, userid, event))
        cn.commit()
        flash("Event deleted")
        return redirect("/events")
    
    db.close()
    cn.close()
    return render_template("events.html")



@app.route("/shop", methods=["GET"])
@login_required
def shop():
    return render_template("shop.html")



@app.route("/interests", methods=["GET", "POST"])
@login_required
def interests():
#connect to database
    cn = mysql.connector.connect(host='localhost', user='root', passwd='abcd', database='gift', auth_plugin='mysql_native_password')
    db = cn.cursor(buffered=True)

#get info for select menu
    db.execute("SELECT id FROM users WHERE id = %s", session['user_id'])
    userid = db.fetchone()[0]
    db.execute("SELECT name FROM people WHERE person_id = %s", [userid])
    people = db.fetchall()
    db.execute("SELECT people.name, interests.interests FROM people JOIN interests ON people.id=interests.interests_id WHERE people.person_id = %s ORDER BY people.name", [userid])
    interests = db.fetchall()

    if request.method == "POST":
#check for user mischief
        name = request.form.get("person")
        if not name:
            flash("Please select person")
            return render_template("interests.html")
        
#get insertion info
        db.execute("SELECT * FROM people WHERE name = %s", [name])
        peopleid = db.fetchone()[0]

#check checkboxes
        interests = request.form.getlist('interests')
        for interest in interests:
            if interest != None:
                db.execute("INSERT INTO interests (interests_id, uinterests_id, interests) VALUES (%s, %s, %s)", (peopleid, userid, interest))
                cn.commit()
        return redirect("/interests")

    cn.close()
    db.close()
    return render_template("interests.html", people=people, interests=interests)
    


@app.route("/custom", methods=["GET", "POST"])
@login_required
def custom():
#connect to database
    cn = mysql.connector.connect(host='localhost', user='root', passwd='abcd', database='gift', auth_plugin='mysql_native_password')
    db = cn.cursor(buffered=True)

#get info for select menu
    db.execute("SELECT id FROM users WHERE id = %s", session['user_id'])
    userid = db.fetchone()[0]
    db.execute("SELECT name FROM people WHERE person_id = %s", [userid])
    people = db.fetchall()

#when viewing form
    if request.method == "POST":

#input custom interest into interests table and into people table
        name = request.form.get("person")
        custom = request.form.get("add")
        db.execute("SELECT id FROM people WHERE name = %s", [name])
        id = db.fetchone()[0]
        if not custom:
            flash("Please input interest")
            return render_template("interests.html")
        elif not name:
            flash("Please select a person")
            return render_template("interests.html")
        else:
            db.execute("INSERT INTO interests (interests_id, uinterests_id, interests) VALUES (%s, %s, %s)", (id, userid, custom))
            cn.commit()
            return redirect("/interests")
    db.close()
    cn.close()
    flash("Interest successfully added")
    return render_template("interests.html", people=people)


@app.route("/deleteInterest", methods=["GET", "POST"])
@login_required
def delete_interest():
#connect to database
    cn = mysql.connector.connect(host='localhost', user='root', passwd='abcd', database='gift', auth_plugin='mysql_native_password')
    db = cn.cursor(buffered=True)

#get form info
    name = request.form.get("name")
    interest = request.form.get("interest")
    db.execute("SELECT id FROM users WHERE id = %s", session['user_id'])
    userid = db.fetchone()[0]
    db.execute("SELECT id FROM people WHERE name = %s", [name])
    personid = db.fetchone()[0]

#delete interest
    db.execute("DELETE FROM interests WHERE uinterests_id = %s AND interests_id = %s AND interests = %s", (userid, personid, interest))
    cn.commit()

    db.close()
    cn.close()
    return redirect("/interests")



if __name__ == '__main__ ':
    app.run(debug=True)