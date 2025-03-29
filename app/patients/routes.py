from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, g
from datetime import datetime, timedelta
import sqlalchemy as sa
from sqlalchemy import func, desc, asc
from app import db
from app.core.models import Patient, Treatment, TreatmentType, Payment, PaymentDetail
from flask_login import login_required, current_user

bp = Blueprint('patients', __name__)

# Global before request to load patient data for sidebar
@bp.before_app_request
def load_patient_data():
    patient_id = request.args.get('patient_id')
    g.patient = None
    g.total_treatment_cost = 0
    g.total_payments = 0
    g.remaining_balance = 0
    
    if patient_id:
        try:
            g.patient = Patient.query.get(int(patient_id))
            if g.patient:
                # Calculate financial metrics
                treatments = Treatment.query.filter_by(patient_id=g.patient.id).all()
                g.total_treatment_cost = sum(t.price for t in treatments) if treatments else 0
                
                payments = []
                for t in treatments:
                    payments.extend(t.payments)
                g.total_payments = sum(p.amount for p in payments) if payments else 0
                
                g.remaining_balance = g.total_treatment_cost - g.total_payments
        except:
            pass

@bp.route('/')
@login_required
def index():
    # Add debug print for authentication status
    print(f"[index] current_user.is_authenticated: {current_user.is_authenticated}")
    print(f"[index] current_user: {current_user}")
    
    # Dashboard stats
    total_patients = Patient.query.count()
    total_treatments = Treatment.query.count()
    
    # Financial overview
    total_income = db.session.query(func.sum(Payment.amount)).scalar() or 0
    
    # Calculate receivables (debt)
    treatments_sum = db.session.query(func.sum(Treatment.price)).scalar() or 0
    payments_sum = total_income
    total_receivables = treatments_sum - payments_sum
    
    # Recent transactions for dashboard
    recent_transactions = []
    
    # Get recent payments
    recent_payments = Payment.query.order_by(desc(Payment.payment_date)).limit(5).all()
    for payment in recent_payments:
        treatment = payment.treatment
        recent_transactions.append({
            'date': payment.payment_date,
            'patient': treatment.patient,
            'description': f"Ödeme: {treatment.treatment_type.name}",
            'amount': payment.amount,
            'type': 'payment'
        })
    
    # Get recent treatments
    recent_treatments = Treatment.query.order_by(desc(Treatment.treatment_date)).limit(5).all()
    for treatment in recent_treatments:
        recent_transactions.append({
            'date': treatment.treatment_date,
            'patient': treatment.patient,
            'description': f"Tedavi: {treatment.treatment_type.name}",
            'amount': treatment.price,
            'type': 'treatment'
        })
    
    # Sort combined list by date
    recent_transactions.sort(key=lambda x: x['date'], reverse=True)
    recent_transactions = recent_transactions[:5]  # Get only most recent 5
    
    # Chart data for last 7 days
    dates = []
    daily_revenues = []
    
    today = datetime.now().date()
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        dates.append(date.strftime('%d/%m'))
        
        # Get payments for this day
        day_start = datetime.combine(date, datetime.min.time())
        day_end = datetime.combine(date, datetime.max.time())
        
        day_revenue = db.session.query(func.sum(Payment.amount))\
            .filter(Payment.payment_date.between(day_start, day_end))\
            .scalar() or 0
            
        daily_revenues.append(day_revenue)
    
    return render_template('index.html', 
                           total_patients=total_patients,
                           total_treatments=total_treatments,
                           total_income=total_income,
                           total_receivables=total_receivables,
                           recent_transactions=recent_transactions,
                           dates=dates,
                           daily_revenues=daily_revenues)

@bp.route('/patients')
@login_required
def list_patients():
    # Get filter parameters
    search = request.args.get('search', '')
    sort_by = request.args.get('sort', 'name')
    is_desc = 'desc' in request.args
    
    # Base query
    query = Patient.query
    
    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            sa.or_(
                Patient.first_name.ilike(search_term),
                Patient.last_name.ilike(search_term),
                Patient.phone.ilike(search_term),
                Patient.tc_no.ilike(search_term)
            )
        )
    
    # Apply sorting
    if sort_by == 'date':
        order_col = Patient.registration_date
    else:  # Default to name
        order_col = Patient.first_name
        
    if is_desc:
        query = query.order_by(desc(order_col))
    else:
        query = query.order_by(asc(order_col))
    
    # Execute query
    patients = query.all()
    
    # Enhance patient objects with additional financial data
    for patient in patients:
        treatments = Treatment.query.filter_by(patient_id=patient.id).all()
        
        # Get last treatment date
        if treatments:
            treatments.sort(key=lambda x: x.treatment_date, reverse=True)
            patient.last_treatment_date = treatments[0].treatment_date
        else:
            patient.last_treatment_date = None
        
        # Calculate balance
        total_treatment_cost = sum(t.price for t in treatments)
        
        total_paid = 0
        for treatment in treatments:
            payments = Payment.query.filter_by(treatment_id=treatment.id).all()
            total_paid += sum(payment.amount for payment in payments)
        
        patient.balance = total_treatment_cost - total_paid
    
    return render_template('patients/list.html', patients=patients)

@bp.route('/patients/add', methods=['GET', 'POST'])
@login_required
def add_patient():
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        tc_no = request.form.get('tc_no')
        address = request.form.get('address')
        notes = request.form.get('notes')
        
        try:
            patient = Patient(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                tc_no=tc_no,
                address=address
            )
            db.session.add(patient)
            db.session.commit()
            flash('Hasta başarıyla eklendi.', 'success')
            return redirect(url_for('patients.view_patient', patient_id=patient.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Hasta eklenirken bir hata oluştu: {str(e)}', 'danger')
            return redirect(url_for('patients.add_patient'))
            
    return render_template('patients/add.html')

@bp.route('/patients/<int:patient_id>')
@login_required
def view_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    treatments = Treatment.query.filter_by(patient_id=patient_id).order_by(desc(Treatment.treatment_date)).all()
    
    # Get all payments for this patient's treatments
    all_payments = []
    
    # Calculate financial summary
    total_treatment_cost = sum(t.price for t in treatments)
    
    total_payments = 0
    for treatment in treatments:
        payments = Payment.query.filter_by(treatment_id=treatment.id).order_by(desc(Payment.payment_date)).all()
        # Add payments to the all_payments list
        all_payments.extend(payments)
        
        total_payments += sum(p.amount for p in payments)
        
        # Add payment status to treatment objects
        treatment_total_paid = sum(p.amount for p in payments)
        treatment.is_paid = treatment_total_paid >= treatment.price
    
    # Sort all payments by payment_date, newest first
    all_payments.sort(key=lambda p: p.payment_date, reverse=True)
    
    remaining_balance = total_treatment_cost - total_payments
    
    # Get treatment types for the modal form
    treatment_types = TreatmentType.query.all()
    
    # Get today's date for the treatment date field
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('patients/view.html', 
                           patient=patient,
                           treatments=treatments,
                           payments=all_payments,
                           total_treatment_cost=total_treatment_cost,
                           total_payments=total_payments,
                           remaining_balance=remaining_balance,
                           treatment_types=treatment_types,
                           today_date=today_date)

@bp.route('/patients/<int:patient_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        patient.first_name = request.form.get('first_name')
        patient.last_name = request.form.get('last_name')
        patient.phone = request.form.get('phone')
        patient.tc_no = request.form.get('tc_no')
        patient.address = request.form.get('address')
        
        try:
            db.session.commit()
            flash('Hasta bilgileri başarıyla güncellendi.', 'success')
            return redirect(url_for('patients.view_patient', patient_id=patient.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Hasta bilgileri güncellenirken bir hata oluştu: {str(e)}', 'danger')
    
    return render_template('patients/edit.html', patient=patient)

@bp.route('/patients/<int:patient_id>/delete', methods=['POST'])
@login_required
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    try:
        # First delete associated treatments and payments
        treatments = Treatment.query.filter_by(patient_id=patient_id).all()
        for treatment in treatments:
            # Delete payments for this treatment
            payments = Payment.query.filter_by(treatment_id=treatment.id).all()
            for payment in payments:
                # Delete payment details if any
                PaymentDetail.query.filter_by(payment_id=payment.id).delete()
                db.session.delete(payment)
            db.session.delete(treatment)
            
        # Then delete the patient
        db.session.delete(patient)
        db.session.commit()
        flash('Hasta ve ilgili tüm kayıtları başarıyla silindi.', 'success')
        return redirect(url_for('patients.list_patients'))
    except Exception as e:
        db.session.rollback()
        flash(f'Hasta silinirken bir hata oluştu: {str(e)}', 'danger')
        return redirect(url_for('patients.view_patient', patient_id=patient_id))

@bp.route('/unpaid-treatments')
@login_required
def unpaid_treatments():
    # Get filter parameters
    search = request.args.get('search', '')
    sort_by = request.args.get('sort', 'date')
    is_desc = 'desc' in request.args
    
    # Get all treatments
    query = Treatment.query.join(Patient).join(TreatmentType)
    
    # Only get unpaid treatments
    # Using a subquery to find treatments with insufficient payments
    unpaid_subquery = db.session.query(
        Treatment.id.label('treatment_id'),
        func.sum(Payment.amount).label('paid_amount')
    ).outerjoin(Payment).group_by(Treatment.id).subquery()
    
    query = query.outerjoin(
        unpaid_subquery, 
        Treatment.id == unpaid_subquery.c.treatment_id
    ).filter(
        sa.or_(
            unpaid_subquery.c.paid_amount.is_(None),
            unpaid_subquery.c.paid_amount < Treatment.price
        )
    )
    
    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            sa.or_(
                Patient.first_name.ilike(search_term),
                Patient.last_name.ilike(search_term)
            )
        )
    
    # Apply sorting
    if sort_by == 'date':
        order_col = Treatment.treatment_date
    elif sort_by == 'amount':
        order_col = Treatment.price
    elif sort_by == 'patient':
        order_col = Patient.first_name
    else:
        order_col = Treatment.treatment_date
        
    if is_desc:
        query = query.order_by(desc(order_col))
    else:
        query = query.order_by(asc(order_col))
    
    # Execute query
    unpaid_treatments = query.all()
    
    # Calculate summary statistics
    total_debt = sum(t.price for t in unpaid_treatments)
    
    # Get unique patients with unpaid treatments
    unique_patients = set(t.patient.id for t in unpaid_treatments)
    average_debt = total_debt / len(unique_patients) if unique_patients else 0
    
    # Enrich treatment objects with payment information
    for treatment in unpaid_treatments:
        payments = Payment.query.filter_by(treatment_id=treatment.id).all()
        paid_amount = sum(p.amount for p in payments)
        treatment.remaining_amount = treatment.price - paid_amount
    
    return render_template('patients/unpaid_treatments.html',
                           unpaid_treatments=unpaid_treatments,
                           total_debt=total_debt,
                           average_debt=average_debt)

@bp.route('/treatments/<int:treatment_id>')
@login_required
def view_treatment(treatment_id):
    treatment = Treatment.query.get_or_404(treatment_id)
    
    # Get payments for this treatment
    payments = Payment.query.filter_by(treatment_id=treatment_id).all()
    
    # Calculate payment summary
    paid_amount = sum(p.amount for p in payments)
    remaining_amount = treatment.price - paid_amount
    is_paid = paid_amount >= treatment.price
    
    # For mixed payments, load payment details
    for payment in payments:
        if payment.payment_method == 'mixed':
            payment.payment_details = PaymentDetail.query.filter_by(payment_id=payment.id).all()
    
    return render_template('patients/view_treatment.html',
                           treatment=treatment,
                           payments=payments,
                           paid_amount=paid_amount,
                           remaining_amount=remaining_amount,
                           is_paid=is_paid)

@bp.route('/patients/<int:patient_id>/treatments/add', methods=['GET', 'POST'])
@login_required
def add_treatment(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    treatment_types = TreatmentType.query.all()
    
    if request.method == 'POST':
        # Get treatment data
        treatment_type_id = request.form.get('treatment_type_id')
        treatment_date = datetime.strptime(request.form.get('treatment_date'), '%Y-%m-%d')
        price = float(request.form.get('price'))
        notes = request.form.get('notes')
        status = request.form.get('status')  # 'paid' or 'unpaid'
        
        try:
            # Create treatment
            treatment = Treatment(
                patient_id=patient_id,
                treatment_type_id=treatment_type_id,
                treatment_date=treatment_date,
                price=price,
                notes=notes
            )
            db.session.add(treatment)
            db.session.commit()
            
            # If marked as paid, also create a payment
            if status == 'paid':
                payment_method = request.form.get('payment_method')
                payment_amount = float(request.form.get('payment_amount'))
                payment_notes = request.form.get('payment_notes')
                
                payment = Payment(
                    treatment_id=treatment.id,
                    amount=payment_amount,
                    payment_date=treatment_date,
                    payment_method=payment_method,
                    notes=payment_notes
                )
                db.session.add(payment)
                
                # For mixed payments, add details
                if payment_method == 'mixed':
                    cash_amount = float(request.form.get('cash_amount'))
                    card_amount = float(request.form.get('card_amount'))
                    
                    cash_detail = PaymentDetail(
                        payment_id=payment.id,
                        payment_type='cash',
                        amount=cash_amount
                    )
                    card_detail = PaymentDetail(
                        payment_id=payment.id,
                        payment_type='credit_card',
                        amount=card_amount
                    )
                    
                    db.session.add(cash_detail)
                    db.session.add(card_detail)
                
                db.session.commit()
            
            flash('Tedavi başarıyla eklendi.', 'success')
            return redirect(url_for('patients.view_patient', patient_id=patient_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Tedavi eklenirken bir hata oluştu: {str(e)}', 'danger')
            return redirect(url_for('patients.add_treatment', patient_id=patient_id))
    
    # For GET request, prepare form
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('patients/add_treatment.html',
                           patient=patient,
                           treatment_types=treatment_types,
                           today_date=today_date)

@bp.route('/treatments/<int:treatment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_treatment(treatment_id):
    treatment = Treatment.query.get_or_404(treatment_id)
    treatment_types = TreatmentType.query.all()
    
    if request.method == 'POST':
        # Update treatment data
        treatment.treatment_type_id = request.form.get('treatment_type_id')
        treatment.treatment_date = datetime.strptime(request.form.get('treatment_date'), '%Y-%m-%d')
        new_price = float(request.form.get('price'))
        treatment.notes = request.form.get('notes')
        
        # Handle price change - update treatment history
        if treatment.price != new_price:
            treatment.price = new_price
        
        try:
            db.session.commit()
            flash('Tedavi bilgileri başarıyla güncellendi.', 'success')
            return redirect(url_for('patients.view_treatment', treatment_id=treatment.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Tedavi güncellenirken bir hata oluştu: {str(e)}', 'danger')
    
    return render_template('patients/edit_treatment.html',
                           treatment=treatment,
                           treatment_types=treatment_types)

@bp.route('/treatments/<int:treatment_id>/delete', methods=['POST'])
@login_required
def delete_treatment(treatment_id):
    treatment = Treatment.query.get_or_404(treatment_id)
    patient_id = treatment.patient_id
    
    try:
        # First delete all payments for this treatment
        payments = Payment.query.filter_by(treatment_id=treatment_id).all()
        for payment in payments:
            # Delete payment details if any
            PaymentDetail.query.filter_by(payment_id=payment.id).delete()
            db.session.delete(payment)
        
        # Then delete the treatment
        db.session.delete(treatment)
        db.session.commit()
        
        flash('Tedavi ve ilgili ödemeler başarıyla silindi.', 'success')
        return redirect(url_for('patients.view_patient', patient_id=patient_id))
    except Exception as e:
        db.session.rollback()
        flash(f'Tedavi silinirken bir hata oluştu: {str(e)}', 'danger')
        return redirect(url_for('patients.view_treatment', treatment_id=treatment_id))

@bp.route('/treatments/<int:treatment_id>/payments/add', methods=['GET', 'POST'])
def add_payment(treatment_id):
    # This route is now deprecated. Use add_payment_for_patient instead.
    # Redirect to the patient page where the modal can be used
    treatment = Treatment.query.get_or_404(treatment_id)
    return redirect(url_for('patients.view_patient', patient_id=treatment.patient_id))

@bp.route('/patients/<int:patient_id>/add-payment', methods=['POST'])
@login_required
def add_payment_for_patient(patient_id):
    """Add a payment directly from the patient profile page"""
    patient = Patient.query.get_or_404(patient_id)
    treatment_id = request.form.get('treatment_id')
    treatment = Treatment.query.get_or_404(treatment_id)
    
    # Verify the treatment belongs to this patient
    if treatment.patient_id != patient_id:
        flash('Bu tedavi bu hastaya ait değil.', 'danger')
        return redirect(url_for('patients.view_patient', patient_id=patient_id))
    
    # Get payment data
    payment_method = 'mixed'  # Always use mixed method
    amount = float(request.form.get('amount'))
    cash_amount = float(request.form.get('cash_amount'))
    card_amount = float(request.form.get('card_amount'))
    notes = request.form.get('notes')
    payment_date = datetime.now()  # Use current date and time
    
    try:
        # Create payment record
        payment = Payment(
            treatment_id=treatment_id,
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            notes=notes
        )
        db.session.add(payment)
        db.session.flush()  # To get payment ID
        
        # Always create payment details for cash and card amounts
        cash_detail = PaymentDetail(
            payment_id=payment.id,
            payment_type='cash',
            amount=cash_amount
        )
        card_detail = PaymentDetail(
            payment_id=payment.id,
            payment_type='credit_card',
            amount=card_amount
        )
        
        db.session.add(cash_detail)
        db.session.add(card_detail)
        
        db.session.commit()
        
        flash('Ödeme başarıyla eklendi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ödeme eklenirken bir hata oluştu: {str(e)}', 'danger')
    
    return redirect(url_for('patients.view_patient', patient_id=patient_id))

@bp.route('/payments/<int:payment_id>/delete', methods=['POST'])
def delete_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    treatment_id = payment.treatment_id
    
    try:
        # Delete payment details if any
        PaymentDetail.query.filter_by(payment_id=payment_id).delete()
        
        # Delete the payment
        db.session.delete(payment)
        db.session.commit()
        
        flash('Ödeme başarıyla silindi.', 'success')
        return redirect(url_for('patients.view_treatment', treatment_id=treatment_id))
    except Exception as e:
        db.session.rollback()
        flash(f'Ödeme silinirken bir hata oluştu: {str(e)}', 'danger')
        return redirect(url_for('patients.view_treatment', treatment_id=treatment_id))

@bp.route('/api/patients/search')
@login_required
def api_search_patients():
    """JSON API endpoint for live patient search"""
    # Get search term
    search = request.args.get('q', '')
    
    # Base query
    query = Patient.query
    
    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            sa.or_(
                Patient.first_name.ilike(search_term),
                Patient.last_name.ilike(search_term),
                Patient.phone.ilike(search_term),
                Patient.tc_no.ilike(search_term)
            )
        )
    
    # Execute query with limit to avoid performance issues
    patients = query.order_by(Patient.first_name).limit(50).all()
    
    # Prepare response data
    result = []
    for patient in patients:
        treatments = Treatment.query.filter_by(patient_id=patient.id).all()
        
        # Get last treatment date
        last_treatment_date = None
        if treatments:
            treatments.sort(key=lambda x: x.treatment_date, reverse=True)
            last_treatment_date = treatments[0].treatment_date.strftime('%d.%m.%Y') if treatments[0].treatment_date else None
        
        # Calculate balance
        total_treatment_cost = sum(t.price for t in treatments)
        
        total_paid = 0
        for treatment in treatments:
            payments = Payment.query.filter_by(treatment_id=treatment.id).all()
            total_paid += sum(payment.amount for payment in payments)
        
        balance = total_treatment_cost - total_paid
        
        # Format the patient data
        patient_data = {
            'id': patient.id,
            'name': f"{patient.first_name} {patient.last_name}",
            'phone': patient.phone,
            'tc_no': patient.tc_no,
            'address': patient.address,
            'registration_date': patient.registration_date.strftime('%d.%m.%Y'),
            'last_treatment_date': last_treatment_date,
            'balance': float(balance) if balance else 0,
            'balance_formatted': f"{balance:.2f} ₺" if balance > 0 else (f"{abs(balance):.2f} ₺ Alacak" if balance < 0 else "-")
        }
        result.append(patient_data)
    
    return jsonify(result)

@bp.route('/api/unpaid-treatments/search')
@login_required
def api_search_unpaid_treatments():
    """JSON API endpoint for live unpaid treatments search"""
    # Get search term
    search = request.args.get('q', '')
    
    # Get all treatments
    query = Treatment.query.join(Patient).join(TreatmentType)
    
    # Only get unpaid treatments
    # Using a subquery to find treatments with insufficient payments
    unpaid_subquery = db.session.query(
        Treatment.id.label('treatment_id'),
        func.sum(Payment.amount).label('paid_amount')
    ).outerjoin(Payment).group_by(Treatment.id).subquery()
    
    query = query.outerjoin(
        unpaid_subquery, 
        Treatment.id == unpaid_subquery.c.treatment_id
    ).filter(
        sa.or_(
            unpaid_subquery.c.paid_amount.is_(None),
            unpaid_subquery.c.paid_amount < Treatment.price
        )
    )
    
    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            sa.or_(
                Patient.first_name.ilike(search_term),
                Patient.last_name.ilike(search_term),
                TreatmentType.name.ilike(search_term)
            )
        )
    
    # Execute query with limit
    unpaid_treatments = query.order_by(desc(Treatment.treatment_date)).limit(50).all()
    
    # Prepare response data
    result = []
    for treatment in unpaid_treatments:
        # Calculate remaining amount
        payments = Payment.query.filter_by(treatment_id=treatment.id).all()
        paid_amount = sum(p.amount for p in payments)
        remaining = treatment.price - paid_amount
        
        # Format the treatment data
        treatment_data = {
            'id': treatment.id,
            'patient_id': treatment.patient.id,
            'patient_name': f"{treatment.patient.first_name} {treatment.patient.last_name}",
            'patient_phone': treatment.patient.phone,
            'patient_registration_date': treatment.patient.registration_date.strftime('%d.%m.%Y'),
            'treatment_type': treatment.treatment_type.name,
            'date': treatment.treatment_date.strftime('%d.%m.%Y'),
            'price': float(treatment.price),
            'price_formatted': f"{treatment.price:.2f} ₺",
            'remaining': float(remaining),
            'remaining_formatted': f"{remaining:.2f} ₺"
        }
        result.append(treatment_data)
    
    return jsonify(result) 