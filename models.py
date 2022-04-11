from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sandboxSite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=False, nullable=False)
    email = db.Column(db.String(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

class Week(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deliveryDate = db.Column(db.DateTime(), nullable=False)

    def __repr__(self):
        return '<Week %r>' % self.deliveryDate

class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    desc = db.Column(db.String(), nullable=False)
    gf = db.Column(db.Boolean(), nullable=False, default=False)
    df = db.Column(db.Boolean(),  nullable=False, default=False)
    vgt = db.Column(db.Boolean(),  nullable=False, default=False)
    vgn = db.Column(db.Boolean(),  nullable=False, default=False)