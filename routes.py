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