from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length
from wtforms import PasswordField, SubmitField, BooleanField, StringField, TextAreaField
from wtforms.fields.html5 import EmailField


class LoginForm(FlaskForm):
    email = EmailField('E-Mail', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log In')


class RegisterForm(FlaskForm):
    email = EmailField('E-Mail', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Password again', validators=[DataRequired()])
    name = StringField('Username', validators=[DataRequired()])
    is_admin = BooleanField('Make admin')
    submit = SubmitField('Register')


class NewsForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=40)])
    description = StringField('Description', validators=[Length(max=100)])
    content = TextAreaField("Content", validators=[Length(min=3, max=8000)])
    to_rabbit = BooleanField('To Rabbit')
    submit = SubmitField('Send.')


class Comment(FlaskForm):
    comment_content = TextAreaField('Comment', validators=[(DataRequired())])
    submit = SubmitField('Send')

