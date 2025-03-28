from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """
    Decorator that checks if the current user is an admin.
    If not, redirects to the homepage with an error message.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Bu sayfaya erişmek için yönetici hakları gereklidir.', 'danger')
            return redirect(url_for('patients.index'))
        return f(*args, **kwargs)
    return decorated_function 