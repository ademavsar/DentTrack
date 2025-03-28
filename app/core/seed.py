from app.core.models import TreatmentType, Patient, Treatment
from app.core.init_treatment_types import TREATMENT_TYPES
from datetime import datetime, timedelta
import random

def seed_treatment_types(db):
    """Seed treatment types if they don't exist"""
    if TreatmentType.query.count() == 0:
        for treatment_data in TREATMENT_TYPES:
            treatment_type = TreatmentType(
                name=treatment_data['name'],
                description=treatment_data.get('description', ''),
                base_price=treatment_data['base_price']
            )
            db.session.add(treatment_type)
        db.session.commit()
        print(f"Added {len(TREATMENT_TYPES)} treatment types")

def seed_test_patients(db, count=10):
    """Seed test patients if they don't exist"""
    if Patient.query.count() == 0:
        for i in range(1, count + 1):
            patient = Patient(
                first_name=f"Test{i}",
                last_name=f"Patient{i}",
                phone=f"555-{i:04d}",
                tc_no=f"{10000000000 + i}",
                address=f"Test Address {i}, Ankara",
                registration_date=datetime.utcnow() - timedelta(days=random.randint(1, 365))
            )
            db.session.add(patient)
        db.session.commit()
        print(f"Added {count} test patients")

def seed_test_treatments(db):
    """Seed test treatments if they don't exist"""
    if Treatment.query.count() == 0:
        # Get all patients and treatment types
        patients = Patient.query.all()
        treatment_types = TreatmentType.query.all()
        
        if not patients or not treatment_types:
            return
            
        for patient in patients:
            # Each patient gets 1-3 random treatments
            num_treatments = random.randint(1, 3)
            for _ in range(num_treatments):
                treatment_type = random.choice(treatment_types)
                price_variation = random.uniform(0.8, 1.2)  # price varies by ±20%
                price = treatment_type.base_price * price_variation
                
                treatment = Treatment(
                    patient_id=patient.id,
                    treatment_type_id=treatment_type.id,
                    treatment_date=datetime.utcnow() - timedelta(days=random.randint(0, 180)),
                    notes=f"Test treatment note for {patient.first_name}",
                    price=round(price, 2)
                )
                db.session.add(treatment)
        db.session.commit()
        print(f"Added treatments for test patients")

def seed_data(db):
    """Main seed function called when SEED_DB is True"""
    print("Seeding database with initial data...")
    seed_treatment_types(db)
    seed_test_patients(db)
    seed_test_treatments(db)
    print("Database seeding complete!") 