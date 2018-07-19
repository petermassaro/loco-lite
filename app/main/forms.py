from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, \
	BooleanField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, ValidationError, \
	Email, EqualTo, Length
from flask_wtf.file import FileField


class QuoteRequestForm(FlaskForm):
	customer = StringField('Name', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired()])
	street = StringField('Street Address', validators=[DataRequired()])
	city = StringField('City', validators=[DataRequired()])
	state = StringField('State', validators=[DataRequired()])
	zip_code = StringField('Zip Code', validators=[DataRequired()])
	phone = StringField('Phone', validators=[DataRequired()])
	time = StringField('Time')
	description = TextAreaField('Description (Optional)')
	submit = SubmitField('Submit')


class JobDataForm(FlaskForm):
	description = TextAreaField("Description")
	estimate = IntegerField("Estimate")
	submit = SubmitField("Submit Job")


class UserInfoForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired()])
	phone = StringField('Phone', validators=[DataRequired()])
	street = StringField('Street Address', validators=[DataRequired()])
	city = StringField('City', validators=[DataRequired()])
	state = StringField('State', validators=[DataRequired()])
	zip_code = StringField('Zip Code', validators=[DataRequired()])
	submit = SubmitField('Submit')


class WorkOrderForm(FlaskForm):
	description = TextAreaField('Description')
	toggleAddress = BooleanField(
		"Use Default Address: ", default='checked', 
		id='address')
	street = StringField('Street Address', validators=[DataRequired()])
	city = StringField('City', validators=[DataRequired()])
	state = StringField('State', validators=[DataRequired()])
	zip_code = StringField('Zip Code', validators=[DataRequired()])
	submit = SubmitField('Submit')


class JobNoteForm(FlaskForm):
	note = TextAreaField('Note')
	image = FileField('Image Upload')
	submit = SubmitField('Submit')


