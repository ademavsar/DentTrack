from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.core.models import User
from app.auth.forms import UserCreateForm
from app.auth.decorators import admin_required

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/users')
@login_required
@admin_required
def users_list():
    """Display list of all users"""
    users = User.query.all()
    return render_template('admin/users.html', title='Kullanıcı Yönetimi', users=users)

@bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """Add a new user"""
    form = UserCreateForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        
        try:
            db.session.commit()
            flash(f'Kullanıcı "{user.username}" başarıyla oluşturuldu.', 'success')
            return redirect(url_for('admin.users_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Kullanıcı oluşturulurken bir hata oluştu: {str(e)}', 'danger')
    
    return render_template('admin/add_user.html', title='Kullanıcı Ekle', form=form) 