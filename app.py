from flask import (Flask, flash, render_template, url_for, request, redirect, session)
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from models import *
from adminFunctions import *
from helpers import apology, login_required, lookup, usd, twod
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

START_DB_FROM_SCRATCH = True

@app.route("/")
def home():
    if START_DB_FROM_SCRATCH:
        db_init()
    users = User.query.all()
    meals = Meal.query.all()
    orders = Order.query.all()
    if ('user_id' in session):
        myUser = User.query.filter(User.id == session["user_id"]).first()
        email = myUser.email
        if (isAdmin()):
            return render_template("adminHome.html", isAdmin=isAdmin(), email=email)
        return render_template("userHome.html", email=email, isAdmin=isAdmin())
    else:
        # return redirect("/login")
        return render_template("guestHome.html", isAdmin=isAdmin())

@app.route("/createOrder", methods=["GET", "POST"])  
@login_required
def createOrder():

    # TODO: flash message if user has already placed an order this week

    meals = Meal.query.filter(Meal.archived == False).all()
    if ('user_id' in session):
        myUser = User.query.filter(User.id == session["user_id"]).first()
        email = myUser.email
    if (request.method == 'GET'):
        return render_template("createOrder.html", meals=meals, email=email, isAdmin=isAdmin())
        
@app.route("/addUser", methods=["GET", "POST"])  
@login_required
def addUser():
    if ('user_id' in session):
        myUser = User.query.filter(User.id == session["user_id"]).first()
        email = myUser.email
    if request.method == "POST":
        message = request.form.get("email")
        return render_template("guestHome.html", message=message, isAdmin=isAdmin())
    return render_template("addUser.html", email=email, isAdmin=isAdmin())

@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    myUser = User.query.filter(User.id == session["user_id"]).first()
    userId = myUser.id
    email = myUser.email
    # users = User.query.filter(User.email.not_in(ADMIN_EMAILS)).paginate(per_page=2000)
    weeks = Week.query.all()
    orders = Order.query.filter(Order.userId == userId).all()
    print(orders)
    return render_template('orderHistory.html', orders=orders, weeks=weeks, email=email, isAdmin=isAdmin())

@app.route("/viewOrder", methods=["GET", "POST"])
@login_required
def viewOrder():
    if request.method == "GET":
        return redirect('/history')
    myOrder = Order.query.filter(Order.id == request.form.get("id")).first()
    myUser = User.query.filter(User.id == session["user_id"]).first()
    for entry in myOrder.entries:
        print(entry)


    userId = myUser.id
    email = myUser.email
    meals = Meal.query.all()
    # users = User.query.filter(User.email.not_in(ADMIN_EMAILS)).paginate(per_page=2000)
    # orders = Order.query.filter(Order.userId == userId).all()
    return render_template('viewOrder.html', order=myOrder, meals=meals, email=email, isAdmin=isAdmin())

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/requestAccess", methods=["GET", "POST"])
def requestAccess():
    if request.method == "POST":
            
        for k,v in request.form.items():
            print(k,v)
        if request.form.get("email"):
            flash('Thanks for your request! You\'ll get an email now and also if/when your request is approved', category='notify')
            msg = Message('New user request', sender = 'deals.meals.wheels@gmail.com', recipients = ADMIN_EMAILS)
            msg.body = "A new user has requested access.\nName: " + request.form.get('name') 
            msg.body += "\nEmail: " + request.form.get('email')
            msg.body += "\n\nTo confirm this user, please visit the Manage Users page"
            mail.send(msg)
            emails=[]
            emails.append(request.form.get('email'))
            print(emails)
            names=[]
            names.append(request.form.get('name'))
            msg2 = Message('Deal on Meals access request', sender = 'deals.meals.wheels@gmail.com', recipients = emails)
            msg2.body = "Hi, " + names[0] + ", thank you for your interest! When your request is approved, you\'ll get an email with instructions to sign on."
            mail.send(msg2)
            return redirect('/')
    return render_template('/requestAccess.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        session.permanent=True
        if not request.form.get("name"):
            return apology("must provide name", 400)
        if not request.form.get("email"):
            return apology("must provide email", 400)
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("passwords no match")

        email=request.form.get("email")
        users = User.query.filter(User.email==email).all()

        if len(users) != 0:
            return apology("user exists", 400)
        else:
            newUser = User(
                email=request.form.get("email"),
                name=request.form.get("name"),
                hashPw=generate_password_hash(request.form.get("password")))
            db.session.add(newUser)
            db.session.commit()
        entries = User.query.filter(User.email==email).all()
        foundUser = User.query.filter(User.email==email).first()
        if len(entries) != 1:
            return apology("Unable to log in", 403)
        session["user_id"] = foundUser.id

        return redirect('/')

    else: # User reached route via GET (as by clicking a link or via redirect)
        return render_template("requestAccess.html", isAdmin=isAdmin())


@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            return apology("must provide email", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        email=request.form.get("email")
        rows = User.query.filter(User.email==email).all()
        #rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        # Ensure username exists and password is correct
        if len(rows) != 1:
            return apology("This email address is not registered", 403)
        if not check_password_hash(rows[0].hashPw, (request.form.get("password"))):
            return apology("invalid password", 403)
        
        # Remember which user has logged in
        session["user_id"] = rows[0].id

        # Redirect user to home page
        return redirect('/')
        # return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return redirect('/')
        

@app.route("/resetPassword/{hash}")
def resetPassword():
    if not request.form.get("email"):
        return render_template("resetPassword.html", isAdmin=isAdmin())


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

if __name__ == '__main__':
    app.run(debug=False, port=5000, host='127.0.0.1')