from app import db
from app.main import bp
from flask import render_template, url_for, flash, redirect, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app.main.forms import QuoteRequestForm, JobDataForm, UserInfoForm, \
	WorkOrderForm, JobNoteForm
from app.models import QuoteRequests, User, JobData, Customer, JobNote
from app.sendSMS import sendSMS, send_email, send_estimate, create_stripe_customer, send_stripe_invoice
from app.decorators import admin_required, permission_required
import datetime as dt 
import stripe
from app.awsHelpers import get_presigned_url, upload_file_to_s3



@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
	form = QuoteRequestForm()
	if form.validate_on_submit():
		quoteRequest = QuoteRequests(customer=form.customer.data, email=form.email.data,
			submit_time=dt.datetime.utcnow(), street=form.street.data,
			city=form.city.data, state=form.state.data, zip_code=form.zip_code.data,
			phone=form.phone.data, time_requested=form.time.data, description=form.description.data,
			status="Active")
		db.session.add(quoteRequest)
		db.session.commit()
		flash('Your quote request has been submitted')
		message = "Customer Inquiry received from {}.  Phone: {}. {}".format(
			quoteRequest.customer,
			quoteRequest.phone,
			quoteRequest.description
			)
		sendSMS(
			User.get_admin_phone(),
			message
			)
		return redirect(url_for('main.index'))
	return render_template('index.html', form=form)



@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
	user = current_user
	form = UserInfoForm()
	if form.validate_on_submit():
		user.name = form.name.data
		user.phone = form.phone.data
		user.street = form.street.data
		user.city = form.city.data
		user.state = form.state.data
		user.zip_code = form.zip_code.data
		db.session.commit()
		flash("Thanks for entering your info!")
		return redirect(url_for('main.profile'))
	if user.name is not None:
		return render_template('profile.html', user=user)
	else:
		return render_template('profileInfo.html', form=form)


@bp.route('/editProfile', methods=['GET', 'POST'])
@login_required
def editProfile():
	user = current_user
	form = UserInfoForm(obj=user)
	if form.validate_on_submit():
		user.name = form.name.data
		user.phone = form.phone.data
		user.street = form.street.data
		user.city = form.city.data
		user.state = form.state.data
		user.zip_code = form.zip_code.data
		db.session.commit()
		return redirect(url_for('main.profile'))
	return render_template('profileInfo.html', form=form)


@bp.route('/workorder', methods=['GET', 'POST'])
@login_required
def workOrder():
	form = WorkOrderForm(obj=current_user)
	if form.validate_on_submit():
		q_request = QuoteRequests(
			customer = current_user.name,
			email = current_user.email,
			submit_time=dt.datetime.utcnow(),
			street = form.street.data,
			city = form.city.data,
			state = form.state.data,
			zip_code = form.zip_code.data,
			phone = current_user.phone,
			status = 'Active',
			description=form.description.data,
			user_id=current_user.id
			)
		db.session.add(q_request)
		db.session.commit()
		flash("Your Request has been submitted")
		message = "Customer Inquiry received from {}.  Phone: {}  {}".format(
			q_request.customer,
			q_request.phone,
			q_request.description)
		sendSMS(
			User.get_admin_phone(),
			message
			)
		return redirect(url_for('main.index'))
	return render_template('workOrder.html', form=form)


@bp.route('/activity', methods=['GET'])
@login_required
def activity():
	q_requests = current_user.quote_request.order_by(QuoteRequests.id.desc()).all()
	return render_template('activity.html', quoteRequests=q_requests)


@bp.route('/editQR/<quoteId>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(quoteId):
	quote = QuoteRequests.query.filter_by(id=quoteId).first()
	form = QuoteRequestForm(obj=quote)
	if form.validate_on_submit():
		quote.customer = form.customer.data
		quote.email = form.email.data
		quote.street = form.street.data
		quote.city = form.city.data
		quote.state = form.state.data
		quote.zip_code = form.zip_code.data
		quote.phone = form.phone.data
		db.session.commit()
		flash('Quote Request for {} has been edited'.format(quote.customer))
		return redirect(url_for('main.quoteRequests', jobStatus='Active'))
	return render_template('quote.html', form=form)


@bp.route('/quoteRequests/<jobStatus>')
@login_required
@admin_required
def quoteRequests(jobStatus):
	page = request.args.get('page', 1, type=int)
	requests = QuoteRequests.query.filter_by(status=jobStatus).order_by(QuoteRequests.submit_time.desc()).paginate(
		page, current_app.config['QRS_PER_PAGE'], False)
	next_url = url_for('main.quoteRequests', jobStatus=jobStatus, page=requests.next_num) \
		if requests.has_next else None
	prev_url = url_for('main.quoteRequests', jobStatus=jobStatus, page=requests.prev_num) \
		if requests.has_prev else None
	return render_template('quotes.html', quoteRequests=requests.items,
		next_url=next_url, prev_url=prev_url)



@bp.route('/jobnotes/<quoteId>', methods=['GET', 'POST'])
@login_required
@admin_required
def jobNotes(quoteId):
	form = JobNoteForm()
	q_request = QuoteRequests.query.filter_by(id=quoteId).first_or_404()
	notes = q_request.notes.order_by(JobNote.id.desc()).all()
	if form.validate_on_submit():
		if not form.image.data:
			image_name = None
		else:
			image_name = form.image.data.filename
		note = JobNote(
			quote_id=quoteId,
			note=form.note.data,
			image_name = image_name,
			time_submitted=dt.datetime.utcnow()
			)
		db.session.add(note)
		db.session.commit()
		file = request.files.get(form.image.name)
		upload_file_to_s3(file, current_app.config['S3_BUCKET'])
		flash("Job Note Submitted")
		return redirect(url_for('main.jobNotes', quoteId=quoteId))
	return render_template('jobNotes.html', form=form, user=current_user, jobNotes=notes)




@bp.route('/delete/<quoteId>', methods=['GET', 'POST'])
@login_required
@admin_required
def deleteJob(quoteId):
	job = QuoteRequests.query.filter_by(id=quoteId).first_or_404()
	items = JobData.query.filter_by(quote_id=quoteId).all()
	for item in items:
		db.session.delete(item)
	db.session.delete(job)
	db.session.commit()
	return redirect(url_for('main.quoteRequests', jobStatus='Active'))


@bp.route('/toggleStatus/<quoteId>', methods=['GET', 'POST'])
@login_required
@admin_required
def toggleStatus(quoteId):
	q_request = QuoteRequests.query.filter_by(id=quoteId).first_or_404()
	if q_request.status == 'Active':
		q_request.status = 'Complete'
	else:
		q_request.status = 'Active'
	db.session.commit()
	return redirect(url_for('main.quoteRequests', jobStatus='Active'))




@bp.route('/jobdata/<quoteId>', methods=['GET', 'POST'])
@login_required
@admin_required
def jobdata(quoteId):
	form = JobDataForm()
	q_request = QuoteRequests.query.filter_by(id=quoteId).first_or_404()
	jobItems = q_request.job.all()
	if form.validate_on_submit():
		jobData = JobData(
			quote_id=quoteId,
			description=form.description.data,
			estimate=form.estimate.data
			)
		db.session.add(jobData)
		db.session.commit()
		flash("Job Detail Submitted")
		return redirect(url_for('main.jobdata', quoteId=jobData.quote_id))
	return render_template('jobdata.html', form=form, quoteRequest=q_request,
		job_items=jobItems)


@bp.route('/editJobData/<quoteId>/<itemId>', methods=['GET', 'POST'])
@login_required
@admin_required
def editJobData(quoteId, itemId):
	data = JobData.query.filter_by(id=itemId).first()
	form = JobDataForm(obj=data)
	if form.validate_on_submit():
		data.quote_id=quoteId
		data.description=form.description.data
		data.estimate=form.estimate.data
		db.session.commit()
		flash('Job detail edited')
		return redirect(url_for('main.jobdata', quoteId=quoteId))
	return render_template('quote.html', form=form)


@bp.route('/smsCustomerDetails/<quoteId>', methods=['GET','POST'])
@login_required
@admin_required
def textCustDetails(quoteId):
	q_request = QuoteRequests.query.filter_by(id=quoteId).first_or_404()
	message = '{}, {}, {}, {}, {}, {}'.format(
		q_request.customer,
		q_request.street,
		q_request.city,
		q_request.state,
		q_request.zip_code,
		q_request.description
		)
	if not current_user.info_complete():
		flash("Please complete your profile to unlock this feature")
	else:
		flash("Job Information sent")
		sendSMS(current_user.phone, message)
	return redirect(url_for('main.quoteRequests', jobStatus='Active'))



@bp.route('/sendEstimate/<quoteId>/<docType>')
@login_required
@admin_required
def sendEstimate(quoteId, docType):
	job_items = JobData.query.filter_by(quote_id=quoteId).all()
	q_request = QuoteRequests.query.filter_by(id=quoteId).first_or_404()
	token = q_request.get_invoice_token()
	send_estimate(q_request, job_items, docType, token)
	flash("{} sent".format(docType))
	return redirect(url_for('main.jobdata', quoteId=quoteId))



@bp.route('/sendInvoice/<quoteId>')
@login_required
@admin_required
def sendInvoice(quoteId):
	q_request = QuoteRequests.query.filter_by(id=quoteId).first_or_404()
	customer = Customer.query.filter_by(email=q_request.email).first()
	if not customer:
		stripe_customer = create_stripe_customer(q_request.email)
		customer = Customer(
			email=q_request.email,
			stripe_id=stripe_customer.id
			)
		db.session.add(customer)
		db.session.commit()

	job_items = JobData.query.filter_by(quote_id=quoteId).all()
	send_stripe_invoice(customer.stripe_id, job_items)
	flash("Invoice Sent")
	return redirect(url_for('main.jobdata', quoteId=quoteId))



@bp.route('/view/<docType>/<token>', methods=['GET', 'POST'])
def viewInvoice(docType, token):
	q_request = QuoteRequests.verify_invoice_token(token)
	if not q_request:
		return redirect(url_for('main.index'))
	jobItems = JobData.query.filter_by(quote_id=q_request.id).all()
	return render_template('invoice.html', quoteRequest=q_request,
		job_items=jobItems, docType=docType, key=current_app.config['STRIPE_PUB_KEY'])


@bp.route('/estimate/<quoteId>/<response>', methods=['GET', 'POST'])
def estimate_response(quoteId, response):
	q_request = QuoteRequests.query.filter_by(id=quoteId).first_or_404()
	if response == 'accept':
		flash("Thanks for accepting! NEWTEMP will be in touch shortly.")
		message = '{} has accepted Estimate. Phone: {} | Desription: {}'.format(
			q_request.customer, q_request.phone, q_request.description)
		sendSMS(User.get_admin_phone(), message)
		q_request.misc = "Estimate Accepted"
	elif response == 'decline':
		flash("Thanks for your interest in NEWTEMP!")
		message ='{} has declined Estimate.'.format(
			q_request.customer)
		sendSMS(User.get_admin_phone(), message)
		q_request.misc = "Estimate Declined"
		q_request.status = 'Declined'
	db.session.commit()
	return redirect(url_for('main.index'))




@bp.route('/pay/<quoteId>')
def payBalance(quoteId):
	q_request = QuoteRequests.query.filter_by(id=quoteId).first_or_404()
	balance_string = str(q_request.generateTotal())
	return render_template('invoicepay.html',
		quoteRequest=q_request,
		key=current_app.config['STRIPE_PUB_KEY'],
		balance=balance_string)



@bp.route('/charge/<quoteId>', methods=['POST'])
def charge(quoteId):
    
	stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
	q_request = QuoteRequests.query.filter_by(id=quoteId).first_or_404()
	amount = q_request.generateTotal(stripe=True)
	customer = Customer.query.filter_by(email=q_request.email).first()
	
	if not customer:
		stripe_customer = create_stripe_customer(q_request.email)
		customer = Customer(
			email=q_request.email,
			stripe_id=stripe_customer.id
			)
		db.session.add(customer)
		db.session.commit()
	else:
		stripe_customer = stripe.Customer.retrieve(customer.stripe_id)

	stripe_customer.source = request.form['stripeToken']
	stripe_customer.save()

	charge = stripe.Charge.create(
        customer=stripe_customer.id,
        amount=amount,
        currency='usd',
        description='Flask Charge'
    )

	flash("Thank you for your payment!")
	q_request.markComplete()
	q_request.paid = True 
	db.session.commit()
	return redirect(url_for('main.index'))