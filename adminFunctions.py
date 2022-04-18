from flask import (Flask, render_template, url_for, request, redirect, session)
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from models import app, User, Meal, Order, db, meal_order
from helpers import apology, login_required, lookup, usd, twod
from werkzeug.security import check_password_hash, generate_password_hash

ADMIN_EMAILS = ["ma.thomask@gmail.com", "abc@abc.abc"]

def isAdmin():
    if ('user_id' not in session):
        return False

    admin = User.query.filter(User.email=="ma.thomask@gmail.com").first()

    if admin.id == session["user_id"]:
        return True
    return False

@app.route("/usersEdit", methods=["GET", "POST"])
def usersEdit():
    if not isAdmin():
        return redirect('/')
    myUser = User.query.filter(User.id == session["user_id"]).first()
    email = myUser.email
    users = User.query.filter(User.email.not_in(ADMIN_EMAILS)).paginate(per_page=2000)
    return render_template('users.html', users=users, email=email, isAdmin=isAdmin())

@app.route("/meals-edit", methods=["GET", "POST"])
@login_required
def mealsEdit():
    myUser = User.query.filter(User.id == session["user_id"]).first()
    email = myUser.email
    if not isAdmin():
        return render_template('home.html', message="You do not have access to this page")
    meals = Meal.query.filter(Meal.archived==False).paginate(per_page=2000)
    return render_template('meals.html', meals=meals, email=email, isAdmin=isAdmin())
    
@app.route("/deleteUser", methods=["GET", "POST"])
def deleteUser():
    if request.method == "POST":
        for k,v in request.form.items():
            print (k,v)
        if (User.query.filter(User.id==request.form.get("id")).count() < 1):
            return render_template("home.html", message="there was an issue", isAdmin=isAdmin())
        User.query.filter_by(id=request.form.get("id")).delete()
        db.session.commit()
    return redirect('/usersEdit')

@app.route("/createMeal", methods=["POST", "GET"])
@login_required
def createMeal():

    myUser = User.query.filter(User.id == session["user_id"]).first()
    email = myUser.email
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
    return render_template("createMeal.html", email=email, isAdmin=isAdmin())

def db_init():
    db.drop_all()
    db.create_all()
    me = User(name="tom", email="tom", hashPw=generate_password_hash("tom"))
    me2 = User(name="tom", email="ma.thomask@gmail.com", hashPw=generate_password_hash("tom"))
    db.session.add(me)
    db.session.add(me2)
    db.session.commit()
    myMeal1 = Meal(title="Pad Thai", desc="Thailand's best known noodles dish. Rice noodles with egg, green onions, bean sprouts and chopped peanuts", gf=True, df=True, vgt=False, vgn=False, archived=False, price="11")
    myMeal2 = Meal(title="Sushi Bowl", desc="This recipe tastes like veggie sushi rolls, but in simplified bowl form! The spicy mayo sauce really takes it to another level. Feel free to play with the toppings to make this bowl taste like your favorite roll. There are a few steps involved, but each one is super simple. Recipe yields 4 sushi bowls, which keep well for leftovers (for best results, slice the avocado just before serving).", gf=True, df=True, vgt=False, vgn=False, archived=False, price="12")
    myMeal3 = Meal(title="Sausage and Peppers", desc="These Italian Sausage and Peppers are a hearty Italian dinner that’s restaurant quality all made in one-pan. With onions and peppers and spicy sausage, this recipe is bursting with flavor. ", gf=True, df=True, vgt=False, vgn=False, archived=False, price="11")
    db.session.add(myMeal1)
    db.session.add(myMeal2)
    db.session.add(myMeal3)
    db.session.commit()
    myOrder1 = Order(userId=1)
    myOrder2 = Order(userId=2)
    myOrder3 = Order(userId=1)
    myOrder4 = Order(userId=2)
    myOrder1.entries.append(myMeal1)
    myOrder1.entries.append(myMeal2)
    myOrder1.entries.append(myMeal3)
    myOrder2.entries.append(myMeal2)
    myOrder2.entries.append(myMeal3)
    myOrder2.entries.append(myMeal1)
    myOrder3.entries.append(myMeal2)
    myOrder3.entries.append(myMeal3)
    myOrder3.entries.append(myMeal1)
    myOrder4.entries.append(myMeal2)
    myOrder4.entries.append(myMeal3)
    myOrder4.entries.append(myMeal1)
    db.session.commit()
    db.session.commit()
    db.session.add(myOrder1)
    db.session.add(myOrder2)
    db.session.add(myOrder3)
    db.session.add(myOrder4)
    db.session.commit()