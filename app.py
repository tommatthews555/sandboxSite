from flask import (Flask, render_template, url_for, request, redirect, session)
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from models import app, User, Meal, Order, db, meal_order
from helpers import apology, login_required, lookup, usd, twod
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

CREATE_FIRST_USER = True

@app.route("/")
def home():
    db.drop_all()
    db.create_all()
    if CREATE_FIRST_USER:
        me = User(name="tom", email="tom", hashPw=generate_password_hash("tom"))
        me2 = User(name="tom", email="ma.thomask@gmail.com", hashPw=generate_password_hash("tom"))
        db.session.add(me)
        db.session.add(me2)
        db.session.commit()
        myMeal1 = Meal(title="Pad Thai", desc="Thailand's best known noodles dish. Rice noodles with egg, green onions, bean sprouts and chopped peanuts", gf=True, df=True, vgt=False, vgn=False, archived=False, price="11")
        myMeal2 = Meal(title="2nd meal", desc="second meal description", gf=True, df=False, vgt=False, vgn=False, archived=False, price="12")
        myMeal3 = Meal(title="3rd meal", desc="third meal description", gf=True, df=True, vgt=True, vgn=False, archived=False, price="11")
        db.session.add(myMeal1)
        db.session.add(myMeal2)
        db.session.add(myMeal3)
        db.session.commit()
        myOrder = Order(userId=1)
        myOrder.entries.append(myMeal1)
        db.session.commit()
        db.session.commit()
        db.session.add(myOrder)
        db.session.commit()
    users = User.query.all()
    meals = Meal.query.all()
    orders = Order.query.all()
    # return redirect('/meals-edit')
    if (not not session.get("user_id")):
        message = session["user_id"]
        return render_template("home.html", message=message)
    else:
        return redirect("/register")

@app.route("/createOrder")  
@login_required
def createOrder():
    meals = Meal.query.all()
    return render_template("createOrder.html", meals=meals)

@app.route("/addUser", methods=["GET", "POST"])  
@login_required
def addUser():
    if request.method == "POST":
        message = request.form.get("email")
        return render_template("home.html", message=message)
    return render_template("addUser.html")

@app.route("/archiveMeal", methods=["GET", "POST"])
def archiveMeal():
    if request.method == "POST":
        for k,v in request.form.items():
            print (k,v)
        if (Meal.query.filter(Meal.id==request.form.get("id")).count() < 1):
            return render_template("home.html", message="there was an issue")
        mealToArchive = Meal.query.filter(Meal.id==request.form.get("id")).first()
        mealToArchive.archived = True
        db.session.commit()
    return redirect('/meals-edit')

@app.route("/createMeal", methods=["POST", "GET"])
def createMeal():
    if request.method == "POST":
        if not request.form.get("mealTitle") or not request.form.get("description"):
            return("Please complete all fields")
        gf = not not request.form.get("gf")
        df = not not request.form.get("df")
        vgn = not not request.form.get("vgn")
        vgt = not not request.form.get("vgt")
        title = request.form.get("mealTitle")
        desc = request.form.get("description")
        db.session.add(Meal(title=title, desc=desc, gf=gf, df=df, vgt=vgt, vgn=vgn, archived=False))
        db.session.commit()
        return redirect('/createMeal')
    return render_template("createMeal.html")

@app.route("/meals-edit", methods=["GET", "POST"])
def mealsEdit():
    if not isAdmin():
        return render_template('home.html', message="You do not have access to this page")
    meals = Meal.query.filter(Meal.archived==False).paginate(per_page=2000)
    return render_template('meals.html', meals=meals)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)

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
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

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
        return redirect('/meals-edit')
        # return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
        

@app.route("/resetPassword/{hash}")
def resetPassword():
    if not request.form.get("email"):
        return render_template("resetPassword.html")


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

def isAdmin():
    if not session.get("user_id"):
        return False

    admin = User.query.filter(User.email=="ma.thomask@gmail.com").first()
    if admin.id == session["user_id"]:
        return True
    return False

if __name__ == '__main__':
    app.run(debug=False, port=5000, host='127.0.0.1')