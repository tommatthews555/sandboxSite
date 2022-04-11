from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from tempfile import mkdtemp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sandboxSite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=False, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    hashPw = db.Column(db.String(), unique=True, nullable=False)

    def __repr__(self):
        return '<Name %r;id %r; email %r>' % (self.name, self.id, self.email)

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