from app import db, create_app
from app.core.models import TreatmentType

# Define treatment types as a constant for use in seeding
TREATMENT_TYPES = [
    {'name': 'Diş Çekimi', 'base_price': 500, 'description': 'Basit diş çekimi işlemi'},
    {'name': 'Dolgu', 'base_price': 400, 'description': 'Diş dolgu işlemi'},
    {'name': 'Kanal Tedavisi', 'base_price': 1200, 'description': 'Kök kanal tedavisi'},
    {'name': 'Diş Taşı Temizliği', 'base_price': 300, 'description': 'Diş taşı temizliği ve parlatma'},
    {'name': 'İmplant', 'base_price': 8000, 'description': 'Dental implant uygulaması'},
    {'name': 'Zirkonyum Kaplama', 'base_price': 2500, 'description': 'Zirkonyum kaplama işlemi'},
    {'name': 'Porselen Kaplama', 'base_price': 2000, 'description': 'Porselen kaplama işlemi'},
]

def init_treatment_types():
    """Initialize treatment types in the database"""
    app = create_app()
    with app.app_context():
        # Check if treatment types already exist
        if TreatmentType.query.count() > 0:
            print("Treatment types already exist. Skipping initialization.")
            return
            
        # Create treatment types
        for treatment_data in TREATMENT_TYPES:
            treatment_type = TreatmentType(
                name=treatment_data['name'],
                description=treatment_data.get('description', ''),
                base_price=treatment_data['base_price']
            )
            db.session.add(treatment_type)
        
        db.session.commit()
        print(f"Added {len(TREATMENT_TYPES)} treatment types to the database.")

if __name__ == '__main__':
    init_treatment_types() 