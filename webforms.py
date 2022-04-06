from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DecimalField, IntegerField, SelectField, SelectMultipleField, TextAreaField, SubmitField
from wtforms.validators import Optional, DataRequired, Length, EqualTo, URL

class AddUserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	username = StringField("Username", validators=[DataRequired(), Length(min=5, max=20)])
	level = IntegerField("Level", validators=[DataRequired()])
	password1 = PasswordField("Password", validators=[DataRequired(), EqualTo('password2', message='Passwords must match!'), Length(min=7, max=20)])
	password2 = PasswordField("Confirm Password")
	submit = SubmitField("Submit")

class UpdateUserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	username = StringField("Username", validators=[DataRequired(), Length(min=5, max=20)])
	level = IntegerField("Level", validators=[DataRequired()])
	submit = SubmitField("Submit")
	
class BookForm(FlaskForm):
	title = StringField('Title', validators=[DataRequired()])
	title_sort = StringField('Sorted Title')
	author = SelectField('Authors', coerce=int)
	series = SelectField('Series', coerce=int)
	series_index = DecimalField("#", validators=[Optional()])
	#tags = SelectMultipleField('Tags', coerce=int)
	isbn = StringField('ISBN', validators=[DataRequired()])
	publisher = SelectField('Publishers', coerce=int)
	wordcount = IntegerField("Wordcount", validators=[DataRequired()])
	cover = StringField("Cover", validators=[Optional(), URL()])
	description = TextAreaField("Description")
	level = IntegerField("Level", validators=[DataRequired()])
	submit = SubmitField("Submit")
	
class ASTPForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	name_sort = StringField("Name Sort")
	level = IntegerField("Level", validators=[DataRequired()])
	submit = SubmitField("Submit")
	