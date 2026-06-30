from flask import Flask, render_template, request, url_for, redirect , flash 
from app import app
from models import db,Trek,User,Booking


@app.route("/")
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register' ,methods=['POST'])
def register_post():
    full_name=request.form.get('name')
    username=request.form.get('username')
    password=request.form.get('password')
    email=request.form.get('email')
    if not username or not password or not email or not full_name:
        flash('Please enter required fields')  
        return redirect(url_for('register'))
    user=User.query.filter_by(username=username).first()
    if user:
        flash('Please choose another username')
        return redirect(url_for('register'))
    new_user=User(name=full_name,username=username,password=password,email=email)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('user_dashboard'))

@app.route('/login',methods=['POST'])
def login_post():
    username=request.form.get('username')
    password=request.form.get('password')
    if not username or not password:
        flash("Please enter required fields")
        return redirect(url_for('login'))
    user=User.query.filter_by(username=username).first()

    if not user:
        flash("Username doesn't exits")
        return redirect(url_for('login'))
    if user.password!=password:
        flash("Invalid password")
        return redirect(url_for('login'))
    return redirect(url_for('user_dashboard'))

@app.route('/user/dashboard')
def user_dashboard():
    return "Hello world"