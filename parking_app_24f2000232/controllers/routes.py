from flask import render_template, redirect, request, session, jsonify, flash
from datetime import datetime
from app import app
from db_config import db
from models.models import User, ParkingLot, ParkingSpot, BookingHistory

@app.route('/')
def index():
    if 'email' in session:
        return redirect('/admin_dashboard' if session['role'] == 'admin' else '/user_dashboard')
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        role = 'user'

        if User.query.filter_by(email=email).first():
            return "Email already registered"

        new_user = User(email=email, password=password, name=name, address=address, pincode=pincode, role=role)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['email'] = user.email
            session['role'] = user.role
            return redirect('/admin_dashboard' if user.role == 'admin' else '/user_dashboard')

        return render_template('login.html', error='INVALID USER')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect('/login')

    lots = ParkingLot.query.all()
    lot_data = []

    for lot in lots:
        booked_count = ParkingSpot.query.filter_by(lot_id=lot.id, is_booked=True).count()
        free_count = ParkingSpot.query.filter_by(lot_id=lot.id, is_booked=False).count()
        lot_data.append({
            'id': lot.id,
            'name': lot.name,
            'booked': booked_count,
            'free': free_count
        })

    total_booked = ParkingSpot.query.filter_by(is_booked=True).count()
    total_free = ParkingSpot.query.filter_by(is_booked=False).count()

    return render_template("admin_dashboard.html",
                       lots=lots,
                       lot_data=lot_data,
                       total_booked=total_booked,
                       total_free=total_free)

@app.route('/add_lot', methods=['GET', 'POST'])
def add_lot():
    if session.get('role') != 'admin':
        return redirect('/login')

    if request.method == 'POST':
        try:
            name = request.form['name']
            location = request.form['location']
            address = request.form['address']
            pincode = int(request.form['pincode'])
            price = float(request.form['price'])
            max_spots = int(request.form['max_spots'])

            lot = ParkingLot(
                name=name,
                location=location,
                address=address,
                pincode=pincode,
                price=price,
                max_spots=max_spots
            )
            db.session.add(lot)
            db.session.commit()

            for i in range(1, max_spots + 1):
                spot = ParkingSpot(spot_number=f"S{i}", lot_id=lot.id)
                db.session.add(spot)

            db.session.commit()
            flash(" Lot added successfully!")
            return redirect('/admin_dashboard')

        except Exception as e:
            return f" Error adding lot: {e}"

    return render_template('add_lot.html')

@app.route('/user_dashboard')
def user_dashboard():
    if session.get('role') != 'user':
        return redirect('/login')

    lots = ParkingLot.query.all()

    user_email = session['email']
    user_spots = ParkingSpot.query.filter_by(booked_by=user_email).all()

    booked_count = len(user_spots)
    free_count = ParkingSpot.query.filter(ParkingSpot.is_booked == False).count()

    return render_template('user_dashboard.html',
                           lots=lots,
                           booked_count=booked_count,
                           free_count=free_count,
                           user_spots=user_spots)


@app.route('/view_spots/<int:lot_id>')
def view_spots(lot_id):
    if 'email' not in session or session.get('role') != 'user':
        return redirect('/login')
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    return render_template('view_spots.html', spots=spots, lot_id=lot_id)


@app.route('/book/<int:spot_id>')
def book_spot(spot_id):
    if session.get('role') != 'user':
        return redirect('/login')
    spot = ParkingSpot.query.get(spot_id)
    if not spot.is_booked:
        spot.is_booked = True
        spot.booked_by = session['email']
        spot.booked_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.session.commit()
    return redirect(f'/view_spots/{spot.lot_id}')

@app.route('/release/<int:spot_id>', methods=['GET', 'POST'])
def release_spot(spot_id):
    if session.get('role') != 'user':
        return redirect('/login')

    spot = ParkingSpot.query.get_or_404(spot_id)
    lot = ParkingLot.query.get(spot.lot_id)

    if spot.booked_by != session['email']:
        flash("You can only release your own booking.")
        return redirect('/user_dashboard')

    booked_time = datetime.strptime(spot.booked_at, '%Y-%m-%d %H:%M:%S')
    now = datetime.now()
    duration_hours = (now - booked_time).total_seconds() / 3600
    estimated_cost = round(duration_hours * lot.price, 2)

    if request.method == 'POST':
        leaving_time = now

        spot.is_booked = False
        spot.booked_by = None
        spot.booked_at = None
        spot.released_at = leaving_time.strftime('%Y-%m-%d %H:%M:%S')
        db.session.commit()

        history = BookingHistory.query.filter_by(
            user_email=session['email'],
            lot_name=lot.name,
            spot_number=spot.spot_number,
            leaving_at=None
        ).first()

        if history:
            history.leaving_at = leaving_time
            history.duration = duration_hours
            history.cost = estimated_cost
            db.session.commit()

        flash(f" Spot released. Duration: {round(duration_hours, 2)} hrs. Cost: ₹{estimated_cost}")
        return redirect('/history')

    return render_template(
        'release_confirm.html',
        spot=spot,
        lot=lot,
        duration=round(duration_hours, 2),
        cost=estimated_cost
    )



@app.route('/history')
def history():
    if session.get('role') != 'user':
        return redirect('/login')
    records = BookingHistory.query.filter_by(user_email=session['email']).all()
    return render_template('booking_history.html', records=records)


@app.route('/view_users')
def view_users():
    if session.get('role') != 'admin':
        return redirect('/login')

    search = request.args.get('search', '')
    if search:
        users = User.query.filter(
            (User.email.contains(search)) | (User.name.contains(search)),
            User.role == 'user'
        ).all()
    else:
        users =[]

    return render_template('view_users.html', users=users)



@app.route('/delete_lot/<int:lot_id>')
def delete_lot(lot_id):
    lot = ParkingLot.query.get(lot_id)
    occupied = ParkingSpot.query.filter_by(lot_id=lot_id, is_booked=True).count()
    if occupied > 0:
        flash(" Cannot delete lot — spots are still occupied.")
        return redirect('/admin_dashboard')
    ParkingSpot.query.filter_by(lot_id=lot_id).delete()
    db.session.delete(lot)
    db.session.commit()
    flash(" Parking lot deleted successfully")
    return redirect('/admin_dashboard')


@app.route('/api/lots')
def lots_api():
    if 'email' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    lots = ParkingLot.query.all()
    return jsonify([
        {
            'id': lot.id,
            'name': lot.name,
            'location': lot.location,
            'price': lot.price,
            'max_spots': lot.max_spots
        } for lot in lots
    ])

@app.route('/admin/view_spots/<int:lot_id>')
def admin_view_spots(lot_id):
    if session.get('role') != 'admin':
        return redirect('/login')
    
    lot = ParkingLot.query.get(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    return render_template('admin_view_spots.html', spots=spots, lot=lot)


@app.route('/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    lot = ParkingLot.query.get(lot_id)
    if request.method == 'POST':
        lot.name = request.form['name']
        lot.location = request.form['location']
        lot.price = float(request.form['price'])
        db.session.commit()
        flash(" Parking lot updated")
        return redirect('/admin_dashboard')
    return render_template('edit_lot.html', lot=lot)

@app.route('/reserve/<int:lot_id>', methods=['GET', 'POST'])
def reserve_form(lot_id):
    if session.get('role') != 'user':
        return redirect('/login')

    lot = ParkingLot.query.get(lot_id)

    if request.method == 'POST':
        car_number = request.form.get('car_number')
        car_model = request.form.get('car_model')

        spot = ParkingSpot.query.filter_by(lot_id=lot_id, is_booked=False).first()
        if not spot:
            flash(" No available spot in this lot.")
            return redirect('/user_dashboard')

        spot.is_booked = True
        spot.booked_by = session['email']
        spot.booked_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.session.commit()

        booking = BookingHistory(
            user_email=session['email'],
            lot_name=lot.name,
            spot_number=spot.spot_number,
            booked_at=datetime.now(),
            car_number=car_number,
            car_model=car_model
        )
        db.session.add(booking)
        db.session.commit()

        flash(f" Spot {spot.spot_number} booked successfully!")
        return redirect('/user_dashboard')

    return render_template('reserve_form.html', lot=lot)

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if session.get('role') != 'admin':
        return redirect('/login')
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect('/view_users')

@app.route('/my_spot')
def my_spot():
    if session.get('role') != 'user':
        return redirect('/login')
    spot = ParkingSpot.query.filter_by(booked_by=session['email'], is_booked=True).first()
    if spot:
        return redirect(f'/view_spots/{spot.lot_id}')
    flash(" You don't have any active bookings.")
    return redirect('/user_dashboard')

@app.route('/my_bookings')
def my_bookings():
    if session.get('role') != 'user':
        return redirect('/login')
    spots = ParkingSpot.query.filter_by(booked_by=session['email'], is_booked=True).all()
    return render_template('my_bookings.html', spots=spots)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'email' not in session or session.get('role') != 'user':
        return redirect('/login')

    user = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        name = request.form.get('name').strip()
        address = request.form.get('address').strip()
        pincode = request.form.get('pincode').strip()

        if not name or not address or not pincode:
            flash(" All fields are required!")
            return redirect('/edit_profile')

        user.name = name
        user.address = address
        user.pincode = pincode
        db.session.commit()
        flash(" Profile updated successfully!")
        return redirect('/user_dashboard')

    return render_template('edit_profile.html', user=user)

@app.route('/api/spots')
def all_spots_api():
    if 'email' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    spots = ParkingSpot.query.all()
    return jsonify([
        {
            'id': spot.id,
            'lot_id': spot.lot_id,
            'spot_number': spot.spot_number,
            'is_booked': spot.is_booked,
            'booked_by': spot.booked_by
        } for spot in spots
    ])

@app.route('/api/spots/<int:lot_id>')
def spots_by_lot_api(lot_id):
    if 'email' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    return jsonify([
        {
            'id': spot.id,
            'spot_number': spot.spot_number,
            'is_booked': spot.is_booked
        } for spot in spots
    ])

@app.route('/api/user_bookings/<email>')
def user_bookings_api(email):
    if 'email' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    spots = ParkingSpot.query.filter_by(booked_by=email, is_booked=True).all()
    return jsonify([
        {
            'lot_id': spot.lot_id,
            'spot_number': spot.spot_number,
            'booked_at': spot.booked_at
        } for spot in spots
    ])

@app.route('/api/user_history/<email>')
def user_history_api(email):
    if 'email' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    records = BookingHistory.query.filter_by(user_email=email).all()
    return jsonify([
        {
            'lot_name': record.lot_name,
            'spot_number': record.spot_number,
            'booked_at': record.booked_at.strftime('%Y-%m-%d %H:%M:%S'),
            'leaving_at': record.leaving_at.strftime('%Y-%m-%d %H:%M:%S') if record.leaving_at else None,
            'duration': record.duration,
            'cost': record.cost
        } for record in records
    ])

@app.route('/api/users')
def users_api():
    if 'email' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    users = User.query.filter_by(role='user').all()
    return jsonify([
        {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'address': user.address,
            'pincode': user.pincode
        } for user in users
    ])
