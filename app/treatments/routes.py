from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.core.models import TreatmentType

bp = Blueprint('treatments', __name__)

@bp.route('/types')
@login_required
def list_types():
    treatment_types = TreatmentType.query.all()
    return render_template('treatments/types.html', treatment_types=treatment_types)

@bp.route('/types/add', methods=['POST'])
@login_required
def add_type():
    name = request.form.get('name')
    description = request.form.get('description', '')
    base_price = float(request.form.get('base_price', 0))
    
    try:
        treatment_type = TreatmentType(
            name=name, 
            description=description,
            base_price=base_price
        )
        db.session.add(treatment_type)
        db.session.commit()
        flash('Tedavi türü başarıyla eklendi.', 'success')
        return redirect(url_for('treatments.list_types'))
    except Exception as e:
        db.session.rollback()
        flash(f'Tedavi türü eklenirken bir hata oluştu: {str(e)}', 'error')
        return redirect(url_for('treatments.list_types'))

@bp.route('/types/<int:type_id>/edit', methods=['POST'])
@login_required
def edit_type(type_id):
    treatment_type = TreatmentType.query.get_or_404(type_id)
    treatment_type.name = request.form.get('name')
    treatment_type.description = request.form.get('description', '')
    treatment_type.base_price = float(request.form.get('base_price', 0))
    
    try:
        db.session.commit()
        flash('Tedavi türü başarıyla güncellendi.', 'success')
        return redirect(url_for('treatments.list_types'))
    except:
        db.session.rollback()
        flash('Tedavi türü güncellenirken bir hata oluştu.', 'error')
        return redirect(url_for('treatments.list_types'))

@bp.route('/types/<int:type_id>/delete', methods=['POST'])
@login_required
def delete_type(type_id):
    treatment_type = TreatmentType.query.get_or_404(type_id)
    
    try:
        db.session.delete(treatment_type)
        db.session.commit()
        flash('Tedavi türü başarıyla silindi.', 'success')
        return redirect(url_for('treatments.list_types'))
    except:
        db.session.rollback()
        flash('Tedavi türü silinirken bir hata oluştu.', 'error')
        return redirect(url_for('treatments.list_types')) 