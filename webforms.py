from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DecimalField, IntegerField, SelectField, SelectMultipleField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, URL

class AddUserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	username = StringField("Username", validators=[DataRequired(), Length(min=5, max=10)])
	level = IntegerField("Level", validators=[DataRequired()])
	password1 = PasswordField("Password", validators=[DataRequired(), EqualTo('password2', message='Passwords must match!'), Length(min=7, max=20)])
	password2 = PasswordField("Confirm Password")
	submit = SubmitField("Submit")

class UpdateUserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	username = StringField("Username", validators=[DataRequired(), Length(min=5, max=10)])
	level = IntegerField("Level", validators=[DataRequired()])
	submit = SubmitField("Submit")
	
class AddBookForm(FlaskForm):
	title = StringField('Title', validators=[DataRequired()])
	author = SelectField('Authors', coerce=int)
	series = SelectField('Series', coerce=int)
	series_index = DecimalField("#")
	tags = SelectMultipleField('Tags', coerce=int)
	isbn = StringField('ISBN', validators=[DataRequired()])
	publisher = SelectField('Publishers', coerce=int)
	wordcount = IntegerField("Wordcount", validators=[DataRequired()])
	cover = StringField("Cover", validators=[URL()])
	description = TextAreaField("Description")
	level = IntegerField("Level", validators=[DataRequired()])
	submit = SubmitField("Submit")

class UpdateBookForm(FlaskForm):
	title = StringField('Title', validators=[DataRequired()])
	author = SelectField('Authors', coerce=int)
	series = SelectField('Series', coerce=int)
	series_index = DecimalField("#")
	tags = SelectMultipleField('Tags', coerce=int)
	isbn = StringField('ISBN', validators=[DataRequired()])
	publisher = SelectField('Publishers', coerce=int)
	wordcount = IntegerField("Wordcount", validators=[DataRequired()])
	cover = StringField("Cover", validators=[URL()])
	description = TextAreaField("Description")
	level = IntegerField("Level", validators=[DataRequired()])
	submit = SubmitField("Submit")
	
class AddASTPForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	level = IntegerField("Level", validators=[DataRequired()])
	submit = SubmitField("Submit")
	
class UpdateASTPForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	level = IntegerField("Level", validators=[DataRequired()])
	submit = SubmitField("Submit")
	