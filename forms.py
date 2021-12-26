from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import  DataRequired, Email, EqualTo, Length

class CreateUserForm(FlaskForm):
	username = StringField(label=('Логин'), validators=[DataRequired(), Length(max=64)])
	first_name = StringField(label=('Имя'), validators=[DataRequired(), Length(max=64)])
	last_name = StringField(label=('Фамилия'), validators=[DataRequired(), Length(max=64)])
	email = StringField(label=('Email'), validators=[DataRequired(), Email(), Length(max=120)])
	password = PasswordField(label=('Пароль'), validators=[DataRequired(), Length(min=8, message='Password should be at least %(min)d characters long')])
	confirm_password = PasswordField(label=('Подтвердите пароль'), validators=[DataRequired(message='*Required'), EqualTo('password', message='Both password fields must be equal!')])
	submit = SubmitField()

class LoginUserForm(FlaskForm):
	username = StringField(label=('Логин'), validators=[DataRequired(), Length(max=64)])
	password = PasswordField(label=('Пароль'), validators=[DataRequired(), Length(min=8, message='Password should be at least %(min)d characters long')])
	submit = SubmitField()

class AddPostForm(FlaskForm):
	title = StringField(label=('Название статьи'), validators=[DataRequired(), Length(max=64)])
	body = TextAreaField(label=('Текст статьи'))
	submit = SubmitField()
