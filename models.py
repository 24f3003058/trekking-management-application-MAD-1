from app import app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db=SQLAlchemy(app)

class User(db.Model):
    __tablename__='users'
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(32), unique=True, nullable=False)
    name=db.Column(db.String(100),nullable=False)
    password=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(100),nullable=False)
    role=db.Column(db.String(50),nullable=False,default='user')
    created_date=db.Column(db.DateTime ,default=datetime.utcnow)
    is_blacklisted = db.Column(db.Boolean, default=False)
    bookings=db.relationship('Booking',backref='user' ,lazy=True ,foreign_keys='Booking.user_id')
    assigned_treks=db.relationship('Trek',backref='assigned_staff',lazy=True,foreign_keys='Trek.assigned_staff_id')

class Trek(db.Model):
    __tablename__='treks'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(120),nullable=False)
    location=db.Column(db.String(300),nullable=False)
    difficulty=db.Column(db.String(30),nullable=False)
    duration=db.Column(db.Integer,nullable=False)
    total_slots=db.Column(db.Integer,nullable=False)
    assigned_staff_id=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=True)
    available_slots=db.Column(db.Integer,nullable=False)
    status=db.Column(db.String(20),nullable=False,default="pending")
    start_date=db.Column(db.Date,nullable=False)
    end_date=db.Column(db.Date,nullable=False)
    description=db.Column(db.Text,nullable=True,default="No description added")
    price=db.Column(db.Float,nullable=False,default=0.0)
    created_at=db.Column(db.DateTime)
    bookings=db.relationship('Booking',backref='trek',lazy=True,foreign_keys='Booking.trek_id')

class Booking(db.Model):
    __tablename__='bookings'
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    trek_id=db.Column(db.Integer,db.ForeignKey('treks.id'),nullable=False)
    booking_date=db.Column(db.DateTime, default=datetime.utcnow)
    status=db.Column(db.String(50),nullable=False ,default='Booked')

with app.app_context():
    db.create_all()
    admin=User.query.filter_by(role='admin').first()
    if not admin:
        admin=User(username='admin',password='admin',name="admin",email='admin@gmail.com',role='admin')
        db.session.add(admin)
        db.session.commit()