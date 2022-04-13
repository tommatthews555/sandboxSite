from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from tempfile import mkdtemp
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sandboxSite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

meal_order = db.Table('meal_order', 
    db.Column('meal_id', db.Integer, db.ForeignKey('meal.id')),
    db.Column('order_id', db.Integer, db.ForeignKey('order.id')),
    db.Column('id', db.Integer, primary_key=True))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=False, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    hashPw = db.Column(db.String(), unique=True, nullable=False)
    orders = db.relationship('Order', backref='user', lazy=True)

    def __repr__(self):
        return '<Name %r;id %r; email %r>' % (self.name, self.id, self.email)

class Meal(db.Model):
    __tablename__ = "meal"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    desc = db.Column(db.String(), nullable=False)
    gf = db.Column(db.Boolean(), nullable=False, default=False)
    df = db.Column(db.Boolean(),  nullable=False, default=False)
    vgt = db.Column(db.Boolean(),  nullable=False, default=False)
    vgn = db.Column(db.Boolean(),  nullable=False, default=False)
    archived = db.Column(db.Boolean(), nullable=False, default=False)
    price = db.Column(db.Integer, nullable=False, default=11)

    def __repr__(self):
        return 'Meal ID: %s, Title: %s, Description: %s' % (self.id, self.title, self.desc)

class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)    
    entries = db.relationship('Meal', secondary=meal_order, backref='orders')

    def __repr__(self):
        user = User.query.filter(User.id==self.userId).first()
        return 'Order ID: %r,  userID: %s, DateTime: %s' % (self.id, self.meal1Qty, user.email, self.date)
