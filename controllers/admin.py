from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort, session, json
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from extensions import db
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.user import User
from models.reservation import Reservation
from datetime import datetime, timedelta
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
@admin_bp.before_request
@login_required
def require_admin():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('user.dashboard'))
@admin_bp.route('/dashboard')
def dashboard():
    total_lots = ParkingLot.query.count()
    total_spots = ParkingSpot.query.count()
    available_spots = ParkingSpot.query.filter_by(status='A').count()
    total_users = User.query.filter_by(is_admin=False).count()
    recent_reservations = Reservation.query.order_by(Reservation.check_in.desc()).limit(5).all()
    parking_lots = ParkingLot.query.all()
    lot_data = []
    for lot in parking_lots:
        lot_data.append({
            'id': lot.id,
            'name': lot.name,
            'total_spots': lot.max_spots,
            'available_spots': lot.available_spots(),
            'price_per_hour': lot.price_per_hour
        })
    return render_template('admin/dashboard.html',
                         total_lots=total_lots,
                         total_spots=total_spots,
                         available_spots=available_spots,
                         total_users=total_users,
                         recent_reservations=recent_reservations,
                         parking_lots=lot_data)
@admin_bp.route('/parking-lots')
def parking_lots():
    lots = ParkingLot.query.all()
    return render_template('admin/parking_lots.html', parking_lots=lots)
@admin_bp.route('/parking-lot/add', methods=['GET', 'POST'])
def add_parking_lot():
    if request.method == 'POST':
        name = request.form.get('name')
        price_per_hour = float(request.form.get('price_per_hour'))
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        max_spots = int(request.form.get('max_spots'))
        parking_lot = ParkingLot(
            name=name,
            price_per_hour=price_per_hour,
            address=address,
            pincode=pincode,
            max_spots=max_spots
        )
        db.session.add(parking_lot)
        db.session.commit()
        for i in range(1, max_spots + 1):
            spot = ParkingSpot(
                spot_number=f"{parking_lot.id}-{i:03d}",
                status='A',
                parking_lot_id=parking_lot.id
            )
            db.session.add(spot)
        db.session.commit()
        flash('Parking lot added successfully!', 'success')
        return redirect(url_for('admin.parking_lots'))
    return render_template('admin/add_parking_lot.html')
@admin_bp.route('/parking-lot/<int:lot_id>/edit', methods=['GET', 'POST'])
def edit_parking_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    if request.method == 'POST':
        occupied_spots = ParkingSpot.query.filter_by(parking_lot_id=lot_id, status='O').count()
        max_spots_input = request.form.get('max_spots')
        if max_spots_input is None:
            new_max_spots = lot.max_spots
        else:
            try:
                new_max_spots = int(max_spots_input)
            except (ValueError, TypeError):
                flash('Invalid number of spots provided', 'danger')
                return redirect(url_for('admin.edit_parking_lot', lot_id=lot_id))
        if new_max_spots < lot.max_spots and occupied_spots > new_max_spots:
            flash(f'Cannot reduce spots below {occupied_spots} as there are {occupied_spots} occupied spots.', 'danger')
            return redirect(url_for('admin.edit_parking_lot', lot_id=lot_id))
        lot.name = request.form.get('name')
        lot.price_per_hour = float(request.form.get('price_per_hour'))
        lot.address = request.form.get('address')
        lot.pincode = request.form.get('pincode')
        if new_max_spots != lot.max_spots:
            current_spot_count = ParkingSpot.query.filter_by(parking_lot_id=lot_id).count()
            if new_max_spots > current_spot_count:
                for i in range(current_spot_count + 1, new_max_spots + 1):
                    spot = ParkingSpot(
                        spot_number=f"{lot_id}-{i:03d}",
                        status='A',
                        parking_lot_id=lot_id
                    )
                    db.session.add(spot)
            elif new_max_spots < current_spot_count:
                available_spots = ParkingSpot.query.filter_by(
                    parking_lot_id=lot_id,
                    status='A'
                ).order_by(ParkingSpot.id.desc()).limit(current_spot_count - new_max_spots).all()
                for spot in available_spots:
                    db.session.delete(spot)
            lot.max_spots = new_max_spots
        db.session.commit()
        flash('Parking lot updated successfully!', 'success')
        return redirect(url_for('admin.parking_lots'))
    return render_template('admin/edit_parking_lot.html', lot=lot)
@admin_bp.route('/parking-lot/<int:lot_id>/delete', methods=['POST'])
def delete_parking_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    if ParkingSpot.query.filter_by(parking_lot_id=lot_id, status='O').count() > 0:
        flash('Cannot delete parking lot with occupied spots!', 'danger')
        return redirect(url_for('admin.parking_lots'))
    ParkingSpot.query.filter_by(parking_lot_id=lot_id).delete()
    db.session.delete(lot)
    db.session.commit()
    flash('Parking lot deleted successfully!', 'success')
    return redirect(url_for('admin.parking_lots'))
@admin_bp.route('/users')
@login_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)
@admin_bp.route('/user/<int:user_id>/block', methods=['POST'])
@login_required
def block_user(user_id):
    user = User.query.get_or_404(user_id)
    reason = request.form.get('reason', 'No reason provided')
    user.block(reason)
    flash(f'User {user.username} has been blocked.', 'success')
    return redirect(url_for('admin.users'))
@admin_bp.route('/user/<int:user_id>/unblock', methods=['POST'])
@login_required
def unblock_user(user_id):
    user = User.query.get_or_404(user_id)
    user.unblock()
    flash(f'User {user.username} has been unblocked.', 'success')
    return redirect(url_for('admin.users'))
@admin_bp.route('/users/<int:user_id>/reservations')
def user_reservations(user_id):
    user = User.query.get_or_404(user_id)
    reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.check_in.desc()).all()
    return render_template('admin/user_reservations.html', user=user, reservations=reservations)
@admin_bp.route('/reservations')
def reservations():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    query = Reservation.query
    status = request.args.get('status')
    if status in ['active', 'completed', 'cancelled', 'reversed']:
        query = query.filter(Reservation.status == status)
    user_id = request.args.get('user_id', type=int)
    if user_id:
        query = query.filter(Reservation.user_id == user_id)
    parking_lot_id = request.args.get('parking_lot_id', type=int)
    if parking_lot_id:
        query = query.join(ParkingSpot).filter(ParkingSpot.parking_lot_id == parking_lot_id)
    date_from = request.args.get('date_from')
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Reservation.check_in >= date_from)
        except ValueError:
            pass
    date_to = request.args.get('date_to')
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            date_to = date_to.replace(hour=23, minute=59, second=59)
            query = query.filter(Reservation.check_in <= date_to)
        except ValueError:
            pass
    sort_by = request.args.get('sort_by', 'check_in')
    sort_order = request.args.get('sort_order', 'desc')
    if sort_by == 'user':
        query = query.join(User)
        order_field = User.username.asc() if sort_order == 'asc' else User.username.desc()
    elif sort_by == 'amount':
        order_field = Reservation.amount.asc() if sort_order == 'asc' else Reservation.amount.desc()
    else:  
        order_field = Reservation.check_in.asc() if sort_order == 'asc' else Reservation.check_in.desc()
    reservations = query.order_by(order_field).paginate(page=page, per_page=per_page, error_out=False)
    users = User.query.filter_by(is_admin=False).order_by(User.username).all()
    parking_lots = ParkingLot.query.order_by(ParkingLot.name).all()
    filters = {
        'status': request.args.get('status', ''),
        'user_id': request.args.get('user_id', ''),
        'parking_lot_id': request.args.get('parking_lot_id', ''),
        'date_from': request.args.get('date_from', ''),
        'date_to': request.args.get('date_to', ''),
        'sort_by': sort_by,
        'sort_order': sort_order
    }
    from flask_wtf.csrf import generate_csrf
    csrf_token = generate_csrf()
    session['_csrf_token'] = csrf_token
    return render_template('admin/reservations.html', 
                         reservations=reservations,
                         users=users,
                         parking_spots=ParkingSpot.query.all(),
                         parking_lots=parking_lots,
                         filters=filters,
                         csrf_token=csrf_token)
@admin_bp.route('/reservations/create', methods=['POST'])
@login_required
def create_reservation():
    form = request.form
    if not form.get('_csrf_token') or form.get('_csrf_token') != session.get('_csrf_token'):
        flash('Invalid form submission. Please try again.', 'danger')
        return redirect(url_for('admin.reservations'))
    try:
        user_id = form.get('user_id')
        parking_spot_id = form.get('parking_spot_id')
        start_time_str = form.get('start_time')
        duration = int(form.get('duration', 1))
        notes = form.get('notes', '')
        if not all([user_id, parking_spot_id, start_time_str, duration]):
            flash('Please fill in all required fields', 'danger')
            return redirect(url_for('admin.reservations'))
        start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
        end_time = start_time + timedelta(hours=duration)
        spot = ParkingSpot.query.get_or_404(parking_spot_id)
        if spot.status != 'A':
            flash('Selected parking spot is not available', 'danger')
            return redirect(url_for('admin.reservations'))
        overlapping = Reservation.query.filter(
            Reservation.parking_spot_id == parking_spot_id,
            Reservation.check_out > start_time,
            Reservation.check_in < end_time,
            Reservation.status != 'cancelled'
        ).first()
        if overlapping:
            flash('The selected time slot is already booked for this parking spot', 'danger')
            return redirect(url_for('admin.reservations'))
        amount = spot.parking_lot.price_per_hour * duration
        reservation = Reservation(
            user_id=user_id,
            parking_spot_id=parking_spot_id,
            check_in=start_time,
            check_out=end_time,
            amount=amount,
            status='active',
            notes=notes,
            created_by=current_user.id
        )
        spot.status = 'O'  
        db.session.add(reservation)
        db.session.commit()
        flash('Reservation created successfully!', 'success')
        return redirect(url_for('admin.reservations'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating reservation: {str(e)}', 'danger')
        return redirect(url_for('admin.reservations'))
@admin_bp.route('/api/reservations/<int:reservation_id>')
@login_required
def get_reservation(reservation_id):
    reservation = Reservation.query.options(
        joinedload(Reservation.user),
        joinedload(Reservation.spot).joinedload(ParkingSpot.parking_lot)
    ).get_or_404(reservation_id)
    reservation_data = {
        'id': reservation.id,
        'user': {
            'id': reservation.user.id,
            'username': reservation.user.username,
            'email': reservation.user.email
        },
        'spot': {
            'id': reservation.spot.id,
            'spot_number': reservation.spot.spot_number,
            'parking_lot': {
                'id': reservation.spot.parking_lot.id,
                'name': reservation.spot.parking_lot.name,
                'address': reservation.spot.parking_lot.address,
                'pincode': reservation.spot.parking_lot.pincode
            }
        } if reservation.spot else None,
        'vehicle_registration': reservation.vehicle_registration,
        'drivers_license': reservation.drivers_license,
        'check_in': reservation.check_in.isoformat() if reservation.check_in else None,
        'check_out': reservation.check_out.isoformat() if reservation.check_out else None,
        'status': getattr(reservation, 'status', 'unknown'),
        'amount': float(reservation.amount) if reservation.amount else 0.0,
        'payment_method': getattr(reservation, 'payment_method', 'Not specified'),
        'payment_status': getattr(reservation, 'payment_status', 'Not paid'),
        'created_at': reservation.created_at.isoformat() if reservation.created_at else None,
        'updated_at': reservation.updated_at.isoformat() if hasattr(reservation, 'updated_at') and reservation.updated_at else None
    }
    return jsonify(reservation_data)
@admin_bp.route('/api/stats')
def api_stats():
    lots = ParkingLot.query.all()
    labels = [lot.name for lot in lots]
    total_spots = [lot.max_spots for lot in lots]
    available_spots = [lot.available_spots() for lot in lots]
    occupied_spots = [lot.occupied_spots() for lot in lots]
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_revenue = []
    dates = []
    for i in range(7):
        date = (datetime.utcnow() - timedelta(days=6-i)).date()
        next_date = date + timedelta(days=1)
        reservations = Reservation.query.filter(
            Reservation.check_in >= datetime.combine(date, datetime.min.time()),
            Reservation.check_in < datetime.combine(next_date, datetime.min.time())
        ).all()
        total = sum(res.amount or 0 for res in reservations)
        daily_revenue.append(float(total))
        dates.append(date.strftime('%a'))
    return jsonify({
        'labels': labels,
        'total_spots': total_spots,
        'available_spots': available_spots,
        'occupied_spots': occupied_spots,
        'revenue_dates': dates,
        'revenue_data': daily_revenue
    })