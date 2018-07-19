from app import db, login
from flask_login import UserMixin, AnonymousUserMixin
import jwt
from time import time
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app.awsHelpers import get_presigned_url




class Permissions:
	ADMIN = 1
	EMPLOYEE = 2
	CUSTOMER = 3


class QuoteRequests(db.Model):
	__tablename__ = 'quoterequests'
	id = db.Column(db.Integer, primary_key=True)
	customer = db.Column(db.String(120), index=True, unique=False)
	email = db.Column(db.String(120), index=True, unique=False)
	submit_time = db.Column(db.DateTime)
	street = db.Column(db.String(120), unique=False)
	city = db.Column(db.String(120), unique=False)
	state = db.Column(db.String(120), unique=False)
	zip_code = db.Column(db.Integer, unique=False)
	phone = db.Column(db.Integer, unique=False)
	time_requested = db.Column(db.String(120), unique=False)
	description = db.Column(db.String(240), unique=False)
	status = db.Column(db.String(120), unique=False)
	paid = db.Column(db.Boolean)
	complete = db.Column(db.Boolean)
	misc = db.Column(db.String(200), unique=False)
	stripe_id = db.Column(db.String(120), unique=False)
	job = db.relationship('JobData', backref='data', lazy='dynamic')
	notes = db.relationship('JobNote', backref='data', lazy='dynamic')
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


	def __repr__(self):
		return '<QuoteRequest {}>'.format(self.customer)


	def generateTotal(self, stripe=False):
		jobItems = JobData.query.filter(JobData.quote_id==self.id).all()
		total = sum(item.estimate for item in jobItems)
		if stripe:
			return total*100
		return total


	def markComplete(self):
		self.status = 'Complete'


	def reOpen(self):
		self.status = 'Active'


	def get_invoice_token(self, expires_in=100000):
		return jwt.encode(
			{'view_invoice' : self.id, 'exp' : time() + expires_in},
			current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')


	@staticmethod
	def verify_invoice_token(token):
		try:
			id = jwt.decode(token, current_app.config['SECRET_KEY'],
				algorithm=['HS256'])['view_invoice']
		except:
			return
		return QuoteRequests.query.get(id)



class Customer(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(120), index=True, unique=True)
	stripe_id = db.Column(db.String(120), unique=True)




class User(UserMixin, db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120))
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	role = db.Column(db.Integer)
	confirmed = db.Column(db.Boolean, default=False)
	phone = db.Column(db.String(20), unique=True)
	street = db.Column(db.String(120), unique=False)
	city = db.Column(db.String(120), unique=False)
	state = db.Column(db.String(120), unique=False)
	zip_code = db.Column(db.String(120), unique=False)
	stripe_id = db.Column(db.String(120))
	quote_request = db.relationship('QuoteRequests',
		backref='data', lazy='dynamic')


	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		if self.access_level is None:
			if self.email in current_app.config['ADMINS']:
				self.role = Permissions.ADMIN
			else:
				self.role = Permissions.CUSTOMER


	def __repr__(self):
		return '<User {}>'.format(self.email)


	def set_role(self, level):
		self.role = level


	def has_access(self, level):
		return self.role is not None and \
			self.role == level


	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)


	def set_password(self, password):
		self.password_hash = generate_password_hash(password)


	def check_password(self, password):
		return check_password_hash(self.password_hash, password)


	def generate_confirmation_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'confirm': self.id}).decode('utf-8')


	@staticmethod
	def get_token_id(token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token.encode('utf-8'))
		except:
			return
		return data.get('confirm')


	def confirm(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token.encode('utf-8'))
		except:
			return False
		if data.get('confirm') != self.id:
			return False
		self.confirmed = True
		db.session.add(self)
		return True


	def generate_reset_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'reset': self.id}).decode('utf-8')


	@staticmethod
	def reset_password(token, new_password):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token.encode('utf-8'))
		except:
			return False
		user = User.query.get(data.get('reset'))
		if user is None:
			return False
		user.password = new_password
		db.session.add(user)
		return True


	def info_complete(self):
		required_fields = [
			self.name, self.street,
			self.city, self.state,
			self.zip_code, self.phone
			]
		if None in required_fields:
			return False
		return True

	@staticmethod
	def get_admin_phone():
		admins = User.query.filter_by(role=Permissions.ADMIN) \
			.all()
		admin_phone = [admin.phone for admin in admins]
		return [n for n in admin_phone if n is not None]




class AnonymousUser(AnonymousUserMixin):
    def has_access(self, level):
        return False

    @property
    def confirmed(self):
        return False

    def is_administrator(self):
        return False


login.anonymous_user = AnonymousUser



class JobData(db.Model):
	__tablename__ = 'jobdata'
	id = db.Column(db.Integer, primary_key=True)
	quote_id = db.Column(db.Integer, db.ForeignKey('quoterequests.id'))
	description = db.Column(db.String(500), unique=False)
	estimate = db.Column(db.Integer)

	def __repr__(self):
		return '<JobData {}>'.format(self.id)



class JobNote(db.Model):
	__tablename__ = 'jobnotes'
	id = db.Column(db.Integer, primary_key=True)
	quote_id = db.Column(db.Integer, db.ForeignKey('quoterequests.id'))
	note = db.Column(db.String(500), unique=False)
	image_name = db.Column(db.String(500), unique=False)
	time_submitted = db.Column(db.DateTime)

	def __repr__(self):
		return '<JobNote {}'.format(self.id)


	@property
	def image_url(self):
		return get_presigned_url(self.image_name)





@login.user_loader
def load_user(id):
	return User.query.get(int(id))