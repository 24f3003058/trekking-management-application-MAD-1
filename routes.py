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
        return render_template('index.html')
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

@app.route('/admin/admin_manage_trek/add',methods=['GET','POST'])
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

@app.route('/admin/admin_manage_trek/<int:trek_id>/edit',methods=['GET','POST'])
def admin_edit_trek():
    if 'user_id' not in session:
        flash('Please login to continue')
        return redirect(url_for('login'))
    if session.get('role')!='admin':
        flash("Access denied! You can't access this web")
        return redirect(url_for('login'))
    trek=Trek.query.filter_by(id=trek_id).first()
    staff_list=User.query.filter_by(role="staff",is_blacklisted=False).all()
    if request.method=='POST':
        trek.name=request.form.get('name',trek.name).strip()
        trek.location=request.form.get('location',trek.location).strip()
        trek.difficulty=request.fron.get('difficulty',trek.difficulty)
        trek.duration=int(request.form.get('duration',trek.duration))
        new_total=int(request.form.get('total_slots',trek.total_slots))
        difference=new_total-trek.total_slots
        trek.total_slots=new_total
        trek.available_slots=max(0,trek.available_slots+difference)
        trek.start=datetime.strptime(request.form.get('start_date'),'%Y-%m-%d').date()
        trek.end_date=datetime.strptime(request.form.get('end_date'),'%Y-%m-%d').date()
        trek.description=request.form.get('description')
        price_str=request.form.get('price',str(trek.price))
        trek.price=float(price_str) if price_str else trek.price
        assigned_staff_id=request.form.get('assigned_staff_id') or None
        trek.assigned_staff_id=int(assigned_staff_id) if assigned_staff_id else None
        trek.status=request.form.get('status',trek.status)
        db.session.commit()
        return redirect(url_for('admin_manage_trek'))
    return render_template('admin/admin_add_trek.html',staff_list=staff_list,trek=trek)

@app.route('/admin/admin_manage_trek/<int:trek_id>/delete',methods=['POST'])
def admin_delete_trek(trek_id):
    if 'user_id' not in session:
        flash('Please login to continue')
        return redirect(url_for('login'))
    if session.get('role')!=admin:
        flash("Access denied! You can't access this webpage")
        return redirect(url_for('login'))
    trek=Trek.query.filter_by(id=trek_id).first()
    Booking.query.filter_by(trek_id=trek_id).delete(synchronize_session=False)
    db.session.delete(trek)
    db.session.commit()
    return redirect(url_for('admin_manage_trek'))

@app.route('/admin/admin_manage_trek/<int:trek_id>/status',methods=['POST'])
def admin_update_trek_status(trek_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('role')!='admin':
        return redirect(url_for('login'))
    trek=trek.query.filter_by(id=trek_id).first()
    new_status=request.form.get('status')
    valid=['Pending','Approved',"Completed",'Closed','Open']
    if new_status in valid:
        trek.status=new_status
        if new_status=='Completed':
            for b in trek.bookings:
                if b.status=='Booked':
                    b.status='Completed'    
        db.session.commit()
    else:
        flash('Invalid status','danger')
    return redirect(url_for('admin_manage_trek'))

@app.route('/admin/manage_staff')
def manage_staff():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('role')!='admin':
        flash("Access denied!")
        return redirect(url_for('login'))
    search=request.args.get('search')
    query=User.query.filter_by(role='staff')
    if search:
        query=query.filter(User.name.ilike(f'%{search}%'))
    staff_list=query.order_by(User.name).all()
    treks=Trek.query.filter(Trek.status.in_(['Pending',"Approved","Open"])).order_by(Trek.name).all()
    return render_template("admin/manage_staff.html",staff_list=staff_list, treks=treks,search=search)

@app.route('/admin/manage_staff/add_staff',methods=['GET','POST'])
def add_staff():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('role')!='admin':
        flash("Access Denied!")
        return redirect(url_for('login'))
    if request.method=='POST':
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        name=request.form.get('name')
        
        staff=User(username=username,email=email,name=name,role='staff',password=password)
        db.session.add(staff)
        db.session.commit()
        flash("Staff member added successfully!",'success')
        return redirect(url_for('manage_staff'))
    return render_template('admin/staff_form.html')

@app.route('/admin/manage_staff/<int:staff_id>/delete',methods=['POST'])
def admin_delete_staff(staff_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('role')!='admin':
        return redirect(url_for('login'))
    staff=User.query.filter_by(id=staff_id,role='staff').first()
    Trek.query.filter_by(assigned_staff_id=staff_id).update(
        {'assigned_staff_id':None},synchronize_session=False
    )
    db.session.delete(staff)
    db.session.commit()
    flash('Staff member removed successfully!','success')
    return redirect(url_for('manage_staff'))

@app.route('/admin/manage_staff/<int:staff_id>/assign',methods=['POST'])
def admin_assign_staff(staff_id):
    if 'user_id' not in session:
        return redirect('login')
    if session.get('role')!='admin':
        return redirect('login')
    staff=User.query.filter_by(id=staff_id,role='staff').first()
    trek_id=request.form.get('trek_id')
    if not trek_id:
        flash('Please select a trek.','danger')
        return redirect(url_for('manage_staff'))
    trek=Trek.query.filter_by(id=int(trek_id)).first()
    trek.assigned_staff_id=staff_id
    db.session.commit()
    flash({staff.name}, " assigned to trek ",{trek.name}, ".","success")
    return redirect(url_for('manage_staff'))


@app.route('/admin/manage_staff/<int:staff_id>/blacklist')
def admin_blacklist_staff(staff_id):
    if 'user_id' not in session:
        return redirect('login')
    if session.get('role')!='admin':
        flash('Access denied! ONly admin can see this page.')
        return render_template('login.html')
    staff=User.query.filter_by(id=staff_id,role='staff').first()
    staff.is_blacklisted=not staff.is_blacklisted
    db.session.commit()
    status='blacklisted' if staff.is_blacklisted else 'activated'
    flash('staff member added successfully!','success')
    return redirect(url_for(''))

@app.route('/admin/bookings')
def admin_bookings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('role')!='admin':
        return redirect(url_for('login'))
    status_filter=request.args.get('status','')
    query=Booking.query
    if status_filter:
        query=query.filter_by(status=status_filter)
    bookings=query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin/admin_bookings.html' ,bookings=bookings,status_filter=status_filter)


@app.route('/user/bookings')
def user_booking():
    if 'user_id' not in session:
        flash("Please login to continue.",'danger')
        return redirect(url_for('login'))
    if session.get('role')!='user':
        flash("Only users can access this website!",'danger')
        return redirect(url_for('login'))
    user_id=session['user_id']
    bookings=(Booking.query.filter_by(user_id=user_id).all())
    return render_template('user/user_booking.html',bookings=bookings)