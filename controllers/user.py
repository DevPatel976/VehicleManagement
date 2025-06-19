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
    
    return render_template('user/release_spot.html', **template_vars)

@user_bp.route('/reservations')
@login_required
def my_reservations():
    from sqlalchemy.orm import joinedload
    from sqlalchemy import or_
    
    search_query = request.args.get('search', '').strip()
    
  
    query = Reservation.query.options(
        joinedload(Reservation.spot).joinedload(ParkingSpot.parking_lot)
    ).filter_by(
        user_id=current_user.id
    )
    
   
    if search_query:
        query = query.join(ParkingSpot).join(ParkingLot).filter(
            or_(
                Reservation.id.like(f'%{search_query}%'),
                ParkingLot.name.ilike(f'%{search_query}%'),
                ParkingSpot.spot_number.ilike(f'%{search_query}%'),
                Reservation.status.ilike(f'%{search_query}%')
            )
        )
    
  
    reservations = query.order_by(Reservation.check_in.desc()).all()
    
   
    for reservation in reservations:
        if reservation.check_out and reservation.check_in:
            duration = reservation.check_out - reservation.check_in
            reservation.duration_minutes = int(duration.total_seconds() / 60)
        else:
            reservation.duration_minutes = 0
            
    return render_template('user/my_reservations.html', 
                         reservations=reservations, 
                         search_query=search_query)
@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        
        if form_type == 'profile_update':
            current_user.full_name = request.form.get('full_name', current_user.full_name)
            current_user.email = request.form.get('email', current_user.email)
            current_user.phone = request.form.get('phone', current_user.phone)
            current_user.username = request.form.get('username', current_user.username)
            
            new_password = request.form.get('new_password')
            if new_password:
                confirm_password = request.form.get('confirm_password')
                if new_password == confirm_password:
                    current_user.set_password(new_password)
                    flash('Password updated successfully!', 'success')
                else:
                    flash('New passwords do not match!', 'danger')
                    return redirect(url_for('user.profile'))
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('user.profile'))
    
    return render_template('user/profile.html')

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