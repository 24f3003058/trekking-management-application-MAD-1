from flask import Flask, render_template, request, url_for, redirect , flash,session
from app import app
from models import db,Trek,User,Booking
from datetime import datetime


@app.route("/")
def index():
    if 'user_id' in session:
        return render_template('index.html')
    else:
        flash('Please login to continue')
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
    
    if not username or not password or not email or not full_name :
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
    session['user_id']=user.id
    session['role']=user.role
    session['name']=user.name
    if user.role=='admin':
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('user_dashboard'))

@app.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id')




@app.route('/user/dashboard')
def user_dashboard():
    if 'user_id' in session:
        return render_template({{url_for('user_dashboard')}})
    else:
        flash('Please login to continue')
        return redirect(url_for('login'))
    

@app.route('/user/user_profile')
def user_profile():
    if 'user_id' in session:
        return render_template({{url_for('user_profile')}})
    else:
        flash('Please login to continue')
        return redirect(url_for('login'))

    session.pop('user_id')
    return redirect(url_for('login'))
    
@app.route('/admin/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session:
        flash('Please login to continue')
        return redirect(url_for('login'))
    if session.get('role')!='admin':
        flash("Access denied! You can't access this web")
        return redirect(url_for('login'))
    total_treks=Trek.query.count()
    total_users=User.query.filter_by(role='user').count()
    total_staff=User.query.filter_by(role='staff').count()
    total_bookings=Booking.query.count()
    active_bookings=Booking.query.filter_by(status='Booked').count()
    open_treks=Trek.query.filter_by(status='Open').count()
    pending_treks=Trek.query.filter_by(status='Pending').count()
    completed_treks=Trek.query.filter_by(status='Completed').count()
    recent_bookings=Booking.query.order_by(Booking.booking_date.desc()).limit(5).all()
    recent_treks=Trek.query.order_by(Trek.created_at.desc()).limit(5).all()
    return render_template('admin/admin_dashboard.html',total_treks=total_treks,
    total_users=total_users,total_staff=total_staff,total_bookings=total_bookings,
    active_bookings=active_bookings,open_treks=open_treks,pending_treks=pending_treks,
    completed_treks=completed_treks,recent_bookings=recent_bookings,recent_treks=recent_treks)


@app.route('/admin/admin_manage_trek')
def admin_manage_trek():
    if 'user_id' not in session:
        flash('Please login to continue')
        return redirect(url_for('login'))
    if session.get('role')!='admin':
        flash("Access denied! You can't access this web")
        return redirect(url_for('login'))
    status_filter=request.args.get('status','')
    search=request.args.get('search','')
    query=Trek.query
    if status_filter:
        query=query.filter_by(status=status_filter)
    if search:
        query=query.filter_by(Trek.name.ilike(f'%{search}%'))
    treks=query.order_by(Trek.created_at.desc()).all()
    staff_list=User.query.filter_by(role='staff',is_blacklisted=False).all()
    return render_template('admin/admin_manage_trek.html',treks=treks,staff_list=staff_list,status_filter=status_filter,search=search)

@app.route('/admin/admin_add_trek',methods=['GET','POST'])
def admin_add_trek():
    if 'user_id' not in session:
        flash('Please login to continue')
        return redirect(url_for('login'))
    if session.get('role')!='admin':
        flash("Access denied! You can't access this web")
        return redirect(url_for('login'))

    staff_list=User.query.filter_by(role="staff",is_blacklisted=False).all()
    if request.method == "POST":
        name=request.form.get('name')
        location=request.form.get('location')
        difficulty=request.form.get('difficulty')
        total_slots=request.form.get('total_slots')
        duration=request.form.get('duration')
        start_date=datetime.strptime(request.form.get("start_date"),'%Y-%m-%d').date()
        end_date=datetime.strptime(request.form.get("end_date"),'%Y-%m-%d').date()
        description=request.form.get('description')
        price=request.form.get('price')
        assigned_staff_id=request.form.get('assigned_staff_id')
        
        if start_date>=end_date:
            flash("Enter correct end date,it should be after start date!")
            return render_template('admin/admin_add_trek',staff_list=staff_list,trek=None)
        slots= int(total_slots)
        choosen_status=request.form.get('status',"Open")
        valid_statuses=['Pending',"Approved",'Open',"Completed","Closed"]
        if choosen_status not in valid_statuses:
            choosen_status='Open'
        trek= Trek(
            name= name,
            location= location,
            difficulty= difficulty,
            duration= duration,
            total_slots= slots,
            available_slots= slots,
            start_date= start_date,
            end_date=  end_date,
            description= description,
            price= price,
            assigned_staff_id= assigned_staff_id  if assigned_staff_id else None ,
            status= choosen_status
            )
        db.session.add(trek)
        db.session.commit()
        return redirect(url_for('admin_manage_trek'))
    return render_template('admin/admin_add_trek.html',staff_list=staff_list,trek=None)


