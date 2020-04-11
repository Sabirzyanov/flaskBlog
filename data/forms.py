from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length
from wtforms import PasswordField, SubmitField, BooleanField, StringField, TextAreaField
from wtforms.fields.html5 import EmailField


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    is_admin = BooleanField('Сделать админом')
    submit = SubmitField('Войти')


class NewsForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired(), Length(min=3, max=40)])
    description = StringField('Краткое описание', validators=[Length(max=100)])
    content = TextAreaField("Контент", validators=[Length(min=3, max=8000)])
    # is_private = BooleanField("Не публичное")
    submit = SubmitField('Отправить')
