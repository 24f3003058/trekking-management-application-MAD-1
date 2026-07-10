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
        session.clear()
        return redirect(url_for('index'))






  
@app.route('/admin/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session:
        flash('Please login to continue')
        return redirect(url_for('login'))
    if session.get('role')!='admin':
        flash("Access denied! You can't access this web")
        return redirect(url_for('login'))
    total_treks_count=Trek.query.count()
    total_users_count=User.query.filter_by(role='user').count()
    total_staff_count=User.query.filter_by(role='staff').count()
    total_bookings_count=Booking.query.count()
    active_bookings=Booking.query.filter_by(status='Booked').count()
    open_treks=Trek.query.filter_by(status='Open').count()
    pending_treks=Trek.query.filter_by(status='Pending').count()
    completed_treks=Trek.query.filter_by(status='Completed').count()
    recent_bookings=Booking.query.order_by(Booking.booking_date.desc()).limit(5).all()
    recent_treks=Trek.query.order_by(Trek.created_at.desc()).limit(5).all()
    return render_template('admin/admin_dashboard.html',total_treks_count=total_treks_count,
    total_users_count=total_users_count,total_staff_count=total_staff_count,total_bookings_count=total_bookings_count,
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
    status_filter=request.args.get('status')
    search=request.args.get('search')
    query=Trek.query
    if status_filter:
        query=query.filter_by(status=status_filter)
    if search:
        query=query.filter(Trek.name.ilike(f'%{search}%'))
    treks=query.all()
    myusers=User.query.filter_by(role='staff',is_blacklisted=False).all()
    return render_template('admin/admin_manage_trek.html',treks=treks,myusers=myusers,status_filter=status_filter,search=search)

@app.route('/admin/admin_manage_trek/add',methods=['GET','POST'])
def admin_add_trek():
    if 'user_id' not in session:
        flash('Please login to continue')
        return redirect(url_for('login'))
    if session.get('role')!='admin':
        flash("Access denied! You can't access this web")
        return redirect(url_for('login'))

    myusers=User.query.filter_by(role="staff",is_blacklisted=False).all()
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
            return render_template('admin/admin_add_trek',myusers=myusers,trek=None)
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
    return render_template('admin/admin_add_trek.html',myusers=myusers,trek=None)

@app.route('/admin/admin_manage_trek/<int:trek_id>/edit',methods=['GET','POST'])
def admin_edit_trek(trek_id):
    if 'user_id' not in session:
        flash('Please login to continue')
        return redirect(url_for('login'))
    if session.get('role')!='admin':
        flash("Access denied! You can't access this web")
        return redirect(url_for('login'))
    trek=Trek.query.filter_by(id=trek_id).first()
    myusers=User.query.filter_by(role="staff",is_blacklisted=False).all()
    if request.method=='POST':
        trek.name=request.form.get('name',trek.name).strip()
        trek.location=request.form.get('location',trek.location).strip()
        trek.difficulty=request.form.get('difficulty',trek.difficulty)
        trek.duration=int(request.form.get('duration',trek.duration))
        new_total=int(request.form.get('total_slots',trek.total_slots))
        difference=new_total-trek.total_slots
        trek.total_slots=new_total
        trek.available_slots=max(0,trek.available_slots+difference)
        trek.start_date=datetime.strptime(request.form.get('start_date'),'%Y-%m-%d').date()
        trek.end_date=datetime.strptime(request.form.get('end_date'),'%Y-%m-%d').date()
        trek.description=request.form.get('description')
        price_str=request.form.get('price',str(trek.price))
        trek.price=float(price_str) if price_str else trek.price
        assigned_staff_id=request.form.get('assigned_staff_id') or None
        trek.assigned_staff_id=int(assigned_staff_id) if assigned_staff_id else None
        trek.status=request.form.get('status',trek.status)
        db.session.commit()
        return redirect(url_for('admin_manage_trek'))
    return render_template('admin/admin_add_trek.html',myusers=myusers,trek=trek)

@app.route('/admin/admin_manage_trek/<int:trek_id>/delete',methods=['POST'])
def admin_delete_trek(trek_id):
    if 'user_id' not in session:
        flash('Please login to continue')
        return redirect(url_for('login'))
    if session.get('role')!='admin':
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
    trek=Trek.query.filter_by(id=trek_id).first()
    new_status=request.form.get('status')
    valid_status=['Pending','Approved',"Completed",'Closed','Open']
    if new_status in valid_status:
        trek.status=new_status
        if new_status=='Completed':
            for b in trek.bookings:
                if b.status=='Booked':
                    b.status='Completed'    
        db.session.commit()
    else:
        flash('Please enter a valid status.','danger')
    return redirect(url_for('admin_manage_trek'))

@app.route('/admin/manage_staff',methods=['GET'])
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
    myusers=query.all()
    treks=Trek.query.filter(Trek.status.in_(['Pending',"Approved","Open"])).order_by(Trek.name).all()
    return render_template("admin/manage_staff.html",myusers=myusers, treks=treks,search=search)

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
        flash('Please choose a trek for this staff','warning')
        return redirect(url_for('manage_staff'))
    trek=Trek.query.filter_by(id=int(trek_id)).first()
    trek.assigned_staff_id=staff_id
    db.session.commit()
    flash("Staff assigned successfully","success")
    return redirect(url_for('manage_staff'))


@app.route('/admin/manage_staff/<int:staff_id>/blacklist', methods=['POST'])
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
    return redirect(url_for('manage_staff'))

@app.route('/admin/search_user', methods=['GET'])
def search_user():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('role')!='admin':
        return redirect(url_for('login'))
    search=request.args.get('search')
    query=User.query.filter_by(role='user')
    
    if search:
        query=query.filter(User.name.ilike(f'%{search}%'))
    users=query.all()
    return render_template('admin/search_user.html',users=users,search=search)


@app.route('/admin/search_users/<int:user_id>/blacklist', methods=['POST'])
def admin_blacklist_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('role')!='admin':
        return redirect(url_for('login'))
    user=User.query.filter_by(id=user_id,role='user').first()
    user.is_blacklisted =not user.is_blacklisted
    db.session.commit()
    if user.is_blacklisted:
        status="blacklisted"
    else:
        status="activate"
    flash(f"User has been {status}.","success")
    return redirect(url_for('search_user'))

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

@app.route('/user/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash('Please login to continue.')
        return redirect(url_for('login'))
    if session.get('role')!='user':
        flash('Access denied only users can login to this website')
        return redirect(url_for('login'))
    user_id=session['user_id']
    user=db.session.get(User,user_id)
    your_booked_treks=[b.trek for b in Booking.query.filter_by(user_id=user_id,status='Booked').all()]
    open_treks=Trek.query.filter_by(status='Open').all()
    booked_count=sum(1 for b in user.bookings if b.status=='Booked')
    completed_count=sum(1 for b in user.bookings if b.status=='Completed')
    cancelled_count=sum(1 for b in user.bookings if b.status=='Cancelled')
    total_open_trek=[b.trek for b in user.bookings if b.status=='Booked' and b.trek.status=='Open']
    return render_template('user/user_dashboard.html',open_treks=open_treks,user=user,booked_count=booked_count,cancelled_count=cancelled_count,completed_count=completed_count,total_open_trek=total_open_trek,your_booked_treks=your_booked_treks)
    

@app.route('/user/user_dashboard/<int:trek_id>/book',methods=['POST'])
def user_booked_trek(trek_id):
    if 'user_id' not in session:
        flash('Please login to continue.')
        return redirect(url_for('login'))
    if session.get('role')!='user':
        flash('Access denied only users can login to this website')
        return redirect(url_for('login'))
    user_id=session['user_id']
    user=db.session.get(User,user_id)
    if user.is_blacklisted:
        flash("Your account is blocked by admin. You can't book any trek.")
        return redirect(url_for('user_dashboard'))

    trek=Trek.query.filter_by(id=trek_id).first()
    slots_already_booked=Booking.query.filter_by(trek_id=trek.id,status='Booked').count()
    actual_slots=max(0,trek.total_slots -slots_already_booked)
    if trek.available_slots!=actual_slots:
        trek.available_slots=actual_slots
        db.session.commit()
    if actual_slots<=0:
        flash("Slots full,can't book any slots",'danger')
        return redirect(url_for('user_trek_info',trek_id=trek_id))

    already_booked=Booking.query.filter_by(user_id=user_id,trek_id=trek_id,status='Booked').first()
    if already_booked:
        flash('this trek is already booked by you!','danger')
        redirect(url_for('user_dashboard'))
    new_booking=Booking(user_id=user_id,trek_id=trek_id,status='Booked')
    trek.available_slots -= 1
    db.session.add(new_booking)
    db.session.commit()
    flash(f'Successfully booked trek to {trek.name} !','success')
    return redirect(url_for('user_dashboard'))

@app.route('/user/user_dashboard/<int:trek_id>/cancel', methods=['POST'])
def user_trek_cancel(trek_id):
    if 'user_id' not in session:
        flash('Please login to continue.')
        return redirect(url_for('login'))
    if session.get('role')!='user':
        flash('Access denied only users can login to this website')
        return redirect(url_for('login'))
    user_id=session['user_id']
    trek=Trek.query.filter_by(id=trek_id).first()
    booking_info=Booking.query.filter_by(trek_id=trek_id,user_id=user_id,status='Booked').first()
    if not booking_info:
        flash("You haven't book this trek.",'danger')
        return redirect(url_for('user_trek_info',trek_id=trek_id))
    booking_info.status='Cancelled'
    db.session.commit()
    booking_done=Booking.query.filter_by(trek_id=trek.id,status='Booked').count()
    after_cancel=max(0,trek.total_slots-booking_done)
    if trek.available_slots != after_cancel:
        trek.available_slots=after_cancel
        db.session.commit()
    flash('Booking cancelled successfully','success')
    return redirect(url_for('user_dashboard'))




@app.route('/user/user_dashboard/<int:trek_id>/trek_detail', methods=['POST'])
def user_trek_info(trek_id):
    if 'user_id' not in session:
        flash('Please login to continue.')
        return redirect(url_for('login'))
    if session.get('role')!='user':
        flash('Access denied only users can login to this website')
        return redirect(url_for('login'))
    user_id=session['user_id']
    user=db.session.get(User,user_id)
    trek=Trek.query.filter_by(id=trek_id).first()
    current_booking=Booking.query.filter_by(user_id=user_id,trek_id=trek_id,status='Booked').first()
    
    return render_template('/user/user_trek_info.html',trek_id=trek.id,trek=trek,current_booking=current_booking)



@app.route('/user/user_profile' ,methods=['GET','POST'])
def user_profile():
    if 'user_id' not in session:
        flash('Please login to continue.')
        return redirect(url_for('login'))
    if session.get('role')!='user':
        flash('Access denied only users can login to this website')
        return redirect(url_for('login'))
    user=db.session.get(User,session['user_id'])
    if request.method=='POST':
        name=request.form.get('name')
        email=request.form.get('email')
        new_password=request.form.get('new_password')
        confirm_password=request.form.get('confirm_password')
        user.name=name
        user.email=email
        if new_password:
            if len(new_password)<6:
                flash("Enter password of atleast 6 characters.")
                booked_count=sum(1 for b in user.bookings if b.status=='Booked')
                completed_count =sum(1 for b in user.bookings if b.status=='Completed')  
                cancelled_count=sum(1 for b in user.bookings if b.status=='Cancelled')
                return render_template('/user/user_profile.html',user=user,booked_count=booked_count,cancelled_count=cancelled_count,completed_count=completed_count)
            user.password=new_password
        db.session.commit()
        session['name']=user.name
        flash('Profile has been updated successfully!')
        return redirect(url_for('user_profile'))
    booked_count=sum(1 for b in user.bookings if b.status=='Booked')
    completed_count =sum(1 for b in user.bookings if b.status=='Completed')  
    cancelled_count=sum(1 for b in user.bookings if b.status=='Cancelled')
    return render_template('/user/user_profile.html',user=user,booked_count=booked_count,cancelled_count=cancelled_count,completed_count=completed_count)
  
@app.route('/user/user_bookings')
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

@app.route('/user/user_bookings/<int:booking_id>/cancel',methods=['POST'])
def user_cancel_booking(booking_id):
    if 'user_id' not in session:
        flash("please login to continue",'danger')
        return redirect(url_for('login'))
    if session.get('role')!='user':
        flash("Access denied! Only users can accesss this website.",'danger')
        return redirect(url_for('login'))
    booking=Booking.query.filter_by(id=booking_id).first()
    if booking.user_id != session['user_id']:
        flash('Access denied','danger')
        return redirect(url_for('user_bookings'))
    
    if booking.status !='Booked':
        flash("You haven't booked this trek, cannot cancel!",'danger')
        return redirect(url_for('user_bookings'))
    trek_id=booking.trek_id
    booking.status='Cancelled'
    db.session.commit()
    """calculating slots again"""
    trek=Booking.trek
    actual_booked=Booking.query.filter_by(trek_id=trek.id, status='Booked').count()
    correct=max(0,trek.total_slots - actual_booked)
    if trek.available_slots!=correct:
        trek.available_slots=correct
        db.session.commit()
        flash("Booking cancelled!",'success')
    return redirect(url_for('user_booking'))



@app.route('/staff/staff_dashboard')
def staff_dashboard():
    if 'user_id' not in session:
        flash('Please login to continue')
        return redirect(url_for('login'))
    if session.get('role')!='staff':
        flash('Access denied! Please login to continue')
        return redirect(url_for('login'))
    user_id=session['user_id']
    assigned_treks=Trek.query.filter_by(assigned_staff_id=user_id).all()
    return render_template('staff/staff_dashboard.html',assigned_treks=assigned_treks)

@app.route('/staff/trek/<int:trek_id>')
def staff_trek_info(trek_id):
    if 'user_id' not in session:
        flash('Please login to continue')
        return redirect(url_for('login'))
    if session.get('role')!='staff':
        flash('Access denied! Please login to continue')
        return redirect(url_for('login'))
    trek=Trek.query.filter_by(id=trek_id).first()
    if trek.assigned_staff_id!=session['user_id']:
        flash('Trek is not assigned for you','danger')
        return redirect(url_for('staff_dashboard'))
    open_bookings= [b for b in trek.bookings if b.status =='Booked']
    return render_template('staff/staff_trek_info.html',trek=trek ,open_bookings=open_bookings)

@app.route('/staff/trek/<int:trek_id>/update',methods=['GET','POST'])
def staff_update_trek(trek_id):
    if 'user_id' not in session:
        flash('Please login to continue')
        return redirect(url_for('login'))
    if session.get('role')!='staff':
        flash('Access denied! Please login to continue')
        return redirect(url_for('login'))
    trek=Trek.query.filter_by(id=trek_id).first()
    if trek.assigned_staff_id != session['user_id']:
        return redirect(url_for("staff_dashboard"))
    new_available_slots=request.form.get('available_slots')
    new_status=request.form.get('status')
    if new_available_slots:
        try:
            slots=int(new_available_slots)
            if 0<=slots<=trek.total_slots:
                trek.available_slots=slots
            else:
                flash(f"Slots must be between 0 and {trek.total_slots}",'danger')
                return redirect(url_for('staff_trek_info',trek_id=trek.id))
        except ValueError:
            flash('Invalid slot count.','danger')
            return redirect(url_for('staff_update_trek',trek_id=trek.id))
    
    if new_status in ("Open","Closed" ,"Completed"):
        trek.status=new_status
        if new_status=='Completed':
            for b in trek.bookings:
                if b.status=='Booked':
                    b.status="Completed"
    db.session.commit()
    flash('Trek updated successfully!','success')
    return redirect(url_for('staff_trek_info',trek_id=trek.id))

@app.route('/staff/trek/<int:trek_id>/total_participants')
def staff_total_participants(trek_id):
    if 'user_id' not in session:
        flash('Please login to continue')
        return redirect(url_for('login'))
    if session.get('role')!='staff':
        flash('Access denied! Please login to continue')
        return redirect(url_for('login'))
    trek=Trek.query.filter_by(id=trek_id).first()
    if trek.assigned_staff_id != session['user_id']:
        flash('This trek is not assigned for you','danger')
        return redirect(url_for('staff_dashboard'))
    active_bookings=Booking.query.filter_by(trek_id=trek.id).all()
    booked_count=sum(1 for b in active_bookings if b.status=='Booked')
    cancelled_count=sum(1 for b in active_bookings if b.status=='Cancelled')
    completed_count=sum(1 for b in active_bookings if b.status=='Completed')
    return render_template('staff/total_participants.html',trek=trek,active_bookings=active_bookings,booked_count=booked_count,cancelled_count=cancelled_count,completed_count=completed_count)

