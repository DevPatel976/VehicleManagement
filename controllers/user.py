from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user, logout_user
from extensions import db
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.reservation import Reservation
from models.user import User
from datetime import datetime, timedelta
user_bp = Blueprint('user', __name__, url_prefix='/user')
@user_bp.before_request
@login_required
def require_login():
    if current_user.is_admin:
        flash('Please log in as a regular user to access this page.', 'danger')
        return redirect(url_for('admin.dashboard'))
@user_bp.route('/dashboard')
def dashboard():
    active_reservations = db.session.query(Reservation).\
        join(ParkingSpot).\
        join(ParkingLot).\
        filter(
            Reservation.user_id == current_user.id,
            Reservation.status == 'active'
        ).all()
    recent_reservations = db.session.query(Reservation).\
        join(ParkingSpot).\
        join(ParkingLot).\
        filter(
            Reservation.user_id == current_user.id
        ).order_by(Reservation.check_in.desc()).limit(5).all()
    total_lots = ParkingLot.query.count()
    total_spots = ParkingSpot.query.count()
    available_spots = ParkingSpot.query.filter_by(status='A').count()
    parking_lots = []
    for lot in ParkingLot.query.all():
        lot_available_spots = ParkingSpot.query.filter_by(
            parking_lot_id=lot.id,
            status='A'
        ).count()
        parking_lots.append({
            'id': lot.id,
            'name': lot.name,
            'available_spots': lot_available_spots,
            'price_per_hour': lot.price_per_hour,
            'address': lot.address
        })
    available_lots = sum(1 for lot in parking_lots if lot['available_spots'] > 0)
    return render_template('user/dashboard.html',
                         active_reservations=active_reservations,
                         reservations=recent_reservations,
                         parking_lots=parking_lots,
                         available_lots=available_lots,
                         total_spots=total_spots)
@user_bp.route('/reserve', methods=['GET', 'POST'])
@login_required
def reserve_spot():
    if request.method == 'GET':
        parking_lots = []
        for lot in ParkingLot.query.all():
            available_spots = ParkingSpot.query.filter_by(
                parking_lot_id=lot.id,
                status='A'
            ).count()
            if available_spots > 0:
                parking_lots.append({
                    'id': lot.id,
                    'name': lot.name,
                    'available_spots': available_spots,
                    'price_per_hour': lot.price_per_hour,
                    'address': lot.address
                })
        return render_template('user/reserve_spot.html', 
                            parking_lots=parking_lots)
    if not request.form.get('csrf_token'):
        flash('Invalid form submission. CSRF token is missing.', 'danger')
        return redirect(url_for('user.reserve_spot'))
    csrf_token = request.form.get('csrf_token')
    from flask_wtf.csrf import validate_csrf
    try:
        validate_csrf(csrf_token)
    except:
        flash('Invalid form submission. Please try again.', 'danger')
        return redirect(url_for('user.reserve_spot'))
    lot_id = request.form.get('lot_id')
    if not lot_id:
        flash('Please select a parking lot.', 'danger')
        return redirect(url_for('user.reserve_spot'))
    existing_reservation = Reservation.query.filter_by(
        user_id=current_user.id,
        status='active'
    ).first()
    if existing_reservation:
        flash('You already have an active reservation!', 'warning')
        return redirect(url_for('user.dashboard'))
    try:
        available_spot = ParkingSpot.query.filter_by(
            parking_lot_id=lot_id,
            status='A'
        ).with_for_update().first()
        if not available_spot:
            flash('No available spots in the selected parking lot!', 'danger')
            return redirect(url_for('user.reserve_spot'))
        available_spot.status = 'O'
        reservation = Reservation(
            user_id=current_user.id,
            spot_id=available_spot.id,
            check_in=datetime.utcnow(),
            status='active'
        )
        db.session.add(reservation)
        db.session.commit()
        flash(f'Spot {available_spot.spot_number} reserved successfully!', 'success')
        return redirect(url_for('user.dashboard'))
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Error in reserve_spot: {str(e)}\n{traceback.format_exc()}")
        flash('An error occurred while processing your reservation. Please try again.', 'danger')
        return redirect(url_for('user.reserve_spot'))
@user_bp.route('/reverse_spot/<int:reservation_id>', methods=['GET', 'POST'])
@login_required
def reverse_spot(reservation_id):
    from forms import ReverseReservationForm
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != current_user.id:
        flash('Unauthorized action!', 'danger')
        return redirect(url_for('user.dashboard'))
    if reservation.status != 'active':
        flash('This spot is already released!', 'warning')
        return redirect(url_for('user.dashboard'))
    form = ReverseReservationForm()
    if form.validate_on_submit():
        try:
            reservation.check_out = datetime.utcnow()
            reservation.amount = 0  
            reservation.status = 'reversed'
            reservation.is_reversed = True
            reservation.reversed_at = datetime.utcnow()
            reservation.reversal_reason = form.reason.data
            reservation.reversal_notes = form.notes.data
            reservation.vehicle_registration = form.vehicle_registration.data
            reservation.drivers_license = form.drivers_license.data
            reservation.spot.status = 'A'
            db.session.commit()
            flash('Parking spot reversed successfully!', 'success')
            return redirect(url_for('user.my_reservations'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while processing your request. Please try again.', 'danger')
    return render_template('user/reverse_spot.html', 
                         form=form, 
                         reservation=reservation,
                         spot=reservation.spot)
@user_bp.route('/release/<int:reservation_id>', methods=['GET', 'POST'])
@login_required
def release_spot(reservation_id):
    from forms import ReleaseSpotForm
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    reservation = Reservation.query.get_or_404(reservation_id)
    spot = reservation.spot
    if reservation.user_id != current_user.id:
        if is_ajax:
            return jsonify({'error': 'Unauthorized action!'}), 403
        flash('Unauthorized action!', 'danger')
        return redirect(url_for('user.dashboard'))
    if reservation.status != 'active':
        if is_ajax:
            return jsonify({'error': 'This spot is already released!', 'redirect': url_for('user.dashboard')})
        flash('This spot is already released!', 'warning')
        return redirect(url_for('user.dashboard'))
    duration = (datetime.utcnow() - reservation.check_in).total_seconds() / 3600  
    amount = round(duration * spot.parking_lot.price_per_hour, 2)
    form = ReleaseSpotForm()
    if request.method == 'POST':
        print(f"Form data: {request.form}")  
        if form.validate_on_submit():
            print("Form validated successfully")  
            try:
                reservation.check_out = datetime.utcnow()
                reservation.amount = amount
                reservation.status = 'completed'
                reservation.vehicle_registration = form.vehicle_registration.data
                reservation.drivers_license = form.drivers_license.data
                spot.status = 'A'
                payment_method = form.payment_method.data
                payment_info = {
                    'method': payment_method,
                    'amount': amount,
                    'timestamp': datetime.utcnow().isoformat()
                }
                if payment_method in ['credit_card', 'debit_card']:
                    payment_info.update({
                        'card_number': form.card_number.data,
                        'card_expiry': form.card_expiry.data,
                        'card_cvv': form.card_cvv.data
                    })
                elif payment_method == 'upi':
                    payment_info.update({
                        'upi_id': form.upi_id.data
                    })
                print(f"Payment info: {payment_info}")  
                db.session.commit()
                if is_ajax:
                    return jsonify({
                        'success': True,
                        'message': f'Spot released successfully! Total amount: ${amount:.2f}',
                        'redirect': url_for('user.dashboard')
                    })
                flash(f'Spot released successfully! Total amount: ${amount:.2f}', 'success')
                return redirect(url_for('user.dashboard'))
            except Exception as e:
                db.session.rollback()
                error_msg = 'An error occurred while processing your request. Please try again.'
                print(f"Error processing release: {str(e)}")  
                if is_ajax:
                    return jsonify({'error': error_msg}), 500
                flash(error_msg, 'danger')
        else:
            print(f"Form validation failed: {form.errors}")  
            if is_ajax:
                return jsonify({
                    'error': 'Please correct the errors in the form.',
                    'errors': form.errors
                }), 400
    template_vars = {
        'form': form,
        'reservation': reservation,
        'spot': spot,
        'duration': round(duration, 2),
        'amount': amount,
        'price_per_hour': spot.parking_lot.price_per_hour
    }
    if is_ajax:
        return jsonify(template_vars)
    return render_template('user/release_spot.html', **template_vars)
@user_bp.route('/reservations')
@login_required
def my_reservations():
    from sqlalchemy.orm import joinedload
    reservations = Reservation.query.options(
        joinedload(Reservation.spot).joinedload(ParkingSpot.parking_lot)
    ).filter_by(
        user_id=current_user.id
    ).order_by(Reservation.check_in.desc()).all()
    for reservation in reservations:
        if reservation.check_out and reservation.check_in:
            duration = reservation.check_out - reservation.check_in
            reservation.duration_minutes = int(duration.total_seconds() / 60)
        else:
            reservation.duration_minutes = 0
    return render_template('user/my_reservations.html', reservations=reservations)
@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type == 'password_change':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            if new_password != confirm_password:
                flash('New passwords do not match!', 'danger')
                return redirect(url_for('user.profile'))
            if not current_user.check_password(current_password):
                flash('Current password is incorrect!', 'danger')
                return redirect(url_for('user.profile'))
            current_user.set_password(new_password)
            db.session.commit()
            flash('Password updated successfully!', 'success')
        elif form_type == 'profile_update':
            current_user.full_name = request.form.get('full_name', current_user.full_name)
            current_user.email = request.form.get('email', current_user.email)
            current_user.phone = request.form.get('phone', current_user.phone)
            current_user.username = request.form.get('username', current_user.username)
            new_password = request.form.get('password')
            if new_password:
                confirm_password = request.form.get('confirm_password')
                if new_password == confirm_password:
                    current_user.set_password(new_password)
                else:
                    flash('New passwords do not match!', 'danger')
                    return redirect(url_for('user.dashboard'))
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('user.dashboard'))
        return redirect(url_for('user.profile'))
    return render_template('user/profile.html')
@user_bp.route('/api/reservation-stats')
def reservation_stats():
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    total_reservations = Reservation.query.filter(
        Reservation.user_id == current_user.id,
        Reservation.check_in >= thirty_days_ago
    ).count()
    reservations = Reservation.query.filter(
        Reservation.user_id == current_user.id,
        Reservation.check_in >= thirty_days_ago,
        Reservation.check_out.isnot(None)
    ).all()
    total_hours = sum(
        (res.check_out - res.check_in).total_seconds() / 3600
        for res in reservations
    )
    total_spent = sum((res.amount or 0) for res in reservations)
    weekly_data = []
    for i in range(4):  
        week_start = datetime.utcnow() - timedelta(weeks=4-i)
        week_end = week_start + timedelta(weeks=1)
        week_reservations = Reservation.query.filter(
            Reservation.user_id == current_user.id,
            Reservation.check_in >= week_start,
            Reservation.check_in < week_end
        ).all()
        weekly_data.append({
            'week': f"Week {4-i}",
            'reservations': len(week_reservations),
            'hours': sum(
                ((res.check_out or datetime.utcnow()) - res.check_in).total_seconds() / 3600
                for res in week_reservations
            )
        })
    return jsonify({
        'total_reservations': total_reservations,
        'total_hours': round(total_hours, 2),
        'total_spent': round(total_spent, 2),
        'weekly_data': weekly_data
    })
@user_bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    try:
        Reservation.query.filter_by(user_id=current_user.id).delete()
        db.session.delete(current_user)
        db.session.commit()
        logout_user()
        flash('Your account has been successfully deleted.', 'success')
        return redirect(url_for('auth.login'))
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting your account. Please try again.', 'danger')
        return redirect(url_for('user.profile'))