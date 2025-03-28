from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=True)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'admin' or 'user'
    is_active = db.Column(db.Boolean(), default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    tc_no = db.Column(db.String(11), nullable=True)
    address = db.Column(db.Text, nullable=True)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    treatments = db.relationship('Treatment', backref='patient', lazy=True)
    
    def __repr__(self):
        return f'{self.first_name} {self.last_name}'

class TreatmentType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    base_price = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return self.name

class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    treatment_type_id = db.Column(db.Integer, db.ForeignKey('treatment_type.id'), nullable=False)
    treatment_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    treatment_type = db.relationship('TreatmentType', backref='treatments')
    payments = db.relationship('Payment', backref='treatment', lazy=True)
    
    # Audit trail alanları
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = db.Column(db.Integer, default=1)
    history = db.relationship('TreatmentHistory', backref='treatment', lazy=True)

class TreatmentHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    treatment_id = db.Column(db.Integer, db.ForeignKey('treatment.id'), nullable=False)
    treatment_date = db.Column(db.DateTime, nullable=False)
    treatment_type_id = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    version = db.Column(db.Integer, nullable=False)
    change_type = db.Column(db.String(20), nullable=False)  # 'update' veya 'delete'

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    treatment_id = db.Column(db.Integer, db.ForeignKey('treatment.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(20), nullable=False)  # 'cash', 'credit_card', 'mixed'
    notes = db.Column(db.Text, nullable=True)
    
    # Audit trail alanları
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = db.Column(db.Integer, default=1)
    history = db.relationship('PaymentHistory', backref='payment', lazy=True)

class PaymentHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    version = db.Column(db.Integer, nullable=False)
    change_type = db.Column(db.String(20), nullable=False)  # 'update' veya 'delete'

class PaymentDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'), nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)  # 'cash' veya 'credit_card'
    amount = db.Column(db.Float, nullable=False)
    payment = db.relationship('Payment', backref='payment_details') 