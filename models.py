from app import db
from flask_login import UserMixin
from app import login
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    phonenumber = db.Column(db.String(11), index=True, unique=True)
    name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    money = db.Column(db.Integer)
    start_station = db.Column(db.Integer)
    end_station = db.Column(db.Integer)
    template = db.Column(db.String(4000) )
    password_hash = db.Column(db.String(128))
    entry_time = db.Column(db.String(15))
    rel = db.relationship('User_travel_history', backref='human', lazy='dynamic') 


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.name) 


@login.user_loader
def load_user(id):
    return User.query.get(int(id))        




class User_travel_history(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(40))
    entry_station = db.Column(db.String(50))
    exit_station = db.Column(db.String(50))
    entry_time = db.Column(db.String(50))
    exit_time = db.Column(db.String(20))
    fare = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
