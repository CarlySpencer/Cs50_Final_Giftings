from flask import Flask, flash, render_template, redirect, request, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("mysql:///giftings.db")
# create an empty database
# insert tables into database
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
        session["user_id"] = rows[0]["id"]
        return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/", methods=["GET", "POST"])
def index():
    # to complete

@app.route("/people", methods=["GET", "POST"])
def people():
    # to complete 

@app.route("/add", methods=["GET", "POST"])
def add():
    # to complete

@app.route("/shop", methods=["GET", "POST"])
def shop():
    # to complete

@app.route("/interests", methods=["GET", "POST"])
def interests():
    # to complete

