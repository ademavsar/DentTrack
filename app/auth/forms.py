from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError
from app.core.models import User

class LoginForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    remember_me = BooleanField('Beni Hatırla')
    submit = SubmitField('Giriş Yap')

class UserCreateForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=3, max=64)])
    email = EmailField('E-posta', validators=[Optional(), Email(), Length(max=120)])
    password = PasswordField('Şifre', validators=[
        DataRequired(),
        Length(min=6, message='Şifre en az 6 karakter olmalıdır.')
    ])
    password2 = PasswordField('Şifreyi Doğrula', validators=[
        DataRequired(),
        EqualTo('password', message='Şifreler eşleşmelidir.')
    ])
    role = SelectField('Rol', choices=[('user', 'Kullanıcı'), ('admin', 'Yönetici')])
    submit = SubmitField('Kullanıcı Oluştur')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Bu kullanıcı adı zaten kullanılıyor.')
            
    def validate_email(self, email):
        if email.data:  # Only validate if email is provided
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Bu e-posta adresi zaten kullanılıyor.')

class UserEditForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=3, max=64)])
    email = EmailField('E-posta', validators=[Optional(), Email(), Length(max=120)])
    password = PasswordField('Yeni Şifre (boş bırakılabilir)', validators=[
        Optional(),
        Length(min=6, message='Şifre en az 6 karakter olmalıdır.')
    ])
    password2 = PasswordField('Şifreyi Doğrula', validators=[
        EqualTo('password', message='Şifreler eşleşmelidir.')
    ])
    role = SelectField('Rol', choices=[('user', 'Kullanıcı'), ('admin', 'Yönetici')])
    is_active = BooleanField('Aktif')
    submit = SubmitField('Kullanıcıyı Güncelle')
    
    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.original_username = kwargs.get('obj', None)
        
    def validate_username(self, username):
        if self.original_username and self.original_username.username != username.data:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Bu kullanıcı adı zaten kullanılıyor.')
                
    def validate_email(self, email):
        if email.data and self.original_username and self.original_username.email != email.data:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Bu e-posta adresi zaten kullanılıyor.') 