from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, current_app
from flask_login import current_user, login_required, login_user, logout_user
from app import db
from app.core.models import User
from app.auth.forms import LoginForm, UserCreateForm, UserEditForm
from urllib.parse import urlparse
from functools import wraps

bp = Blueprint('auth', __name__, url_prefix='/auth')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Bu sayfaya erişmek için yönetici hakları gereklidir.', 'danger')
            return redirect(url_for('patients.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
def login():
    print("\n[login_route] Starting login process")
    print(f"[login_route] current_user.is_authenticated: {current_user.is_authenticated}")
    
    if current_user.is_authenticated:
        print(f"[login_route] User is already authenticated: {current_user}")
        return redirect(url_for('patients.index'))
    
    form = LoginForm()
    print(f"[login_route] Form created, validate_on_submit: {form.validate_on_submit()}")
    
    if form.validate_on_submit():
        print(f"[login_route] Form validation successful")
        print(f"[login_route] Username from form: {form.username.data}")
        
        user = User.query.filter_by(username=form.username.data).first()
        print(f"[login_route] User found in database: {user}")
        
        if user is None or not user.check_password(form.password.data):
            print(f"[login_route] Authentication failed")
            if user is None:
                print(f"[login_route] User not found in database")
            else:
                print(f"[login_route] Password check failed")
            
            flash('Geçersiz kullanıcı adı veya şifre', 'danger')
            return redirect(url_for('auth.login'))
        
        print(f"[login_route] Authentication successful, calling login_user")
        login_user(user, remember=form.remember_me.data)
        print(f"[login_route] After login_user, current_user: {current_user}")
        print(f"[login_route] current_user.is_authenticated: {current_user.is_authenticated}")
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('patients.index')
        
        print(f"[login_route] Redirecting to: {next_page}")
        flash(f'Hoş geldiniz, {user.username}!', 'success')
        return redirect(next_page)
    else:
        if form.errors:
            print(f"[login_route] Form validation errors: {form.errors}")
    
    return render_template('auth/login.html', title='Giriş Yap', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/users')
@login_required
@admin_required
def users_list():
    users = User.query.all()
    return render_template('auth/users.html', title='Kullanıcı Yönetimi', users=users)

@bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
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
            return redirect(url_for('auth.users_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Kullanıcı oluşturulurken bir hata oluştu: {str(e)}', 'danger')
    
    return render_template('auth/add_user.html', title='Kullanıcı Ekle', form=form)

@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserEditForm(obj=user)
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        user.is_active = form.is_active.data
        
        if form.password.data:
            user.set_password(form.password.data)
        
        try:
            db.session.commit()
            flash(f'Kullanıcı "{user.username}" başarıyla güncellendi.', 'success')
            return redirect(url_for('auth.users_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Kullanıcı güncellenirken bir hata oluştu: {str(e)}', 'danger')
    
    return render_template('auth/edit_user.html', title='Kullanıcı Düzenle', form=form, user=user)

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('Kendinizi silemezsiniz.', 'danger')
        return redirect(url_for('auth.users_list'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'Kullanıcı "{user.username}" başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Kullanıcı silinirken bir hata oluştu: {str(e)}', 'danger')
    
    return redirect(url_for('auth.users_list'))

@bp.route('/test-auth')
def test_auth():
    """A diagnostic route to check authentication state"""
    auth_data = {
        "is_authenticated": current_user.is_authenticated,
        "user": str(current_user) if current_user.is_authenticated else "Anonymous",
        "login_manager_active": bool(current_app.login_manager),
        "login_view": current_app.login_manager.login_view,
    }
    
    print(f"[test-auth] Authentication data: {auth_data}")
    return jsonify(auth_data) 