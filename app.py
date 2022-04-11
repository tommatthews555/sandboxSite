from flask import (Flask, render_template, url_for, request, redirect)
from flask_sqlalchemy import SQLAlchemy
from models import app, User, Week, Meal, db

@app.route("/")
def home():
    #db.drop_all()
    db.create_all()
    me = User(username="tom", email="tom@tom.tom")
    db.session.add(me)
    db.session.commit()
    users = User.query.all()
    weeks = Week.query.all()
    meals = Meal.query.all()
    return render_template("home.html", users=users, weeks=weeks, meals=meals)

if __name__ == '__main__':
    app.run(debug=False, port=5000, host='127.0.0.1')