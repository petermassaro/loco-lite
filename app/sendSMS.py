from twilio.rest import Client
from flask import current_app
from threading import Thread 
from flask_mail import Message
from flask import render_template
from app import mail
import stripe






def send_async_text(app, client, msg, recipientNumber):
	with app.app_context():
		if type(recipientNumber) == list:
			for recipient in recipientNumber:
				send(client, msg, recipient)
		else:
			send(client, msg, recipientNumber)

def send(client, msg, recipientNumber):
	client.api.account.messages.create(
		to='+1{}'.format(recipientNumber),
			from_=current_app.config['TWILIO_NUMBER'],
			body=msg
			)

def sendSMS(recipientNumber, messageContent):
	client = Client(
		current_app.config['TWILIO_ACCOUNT_SID'],
		current_app.config['TWILIO_AUTH_TOKEN']
		)
	Thread(target=send_async_text,
		args=(current_app._get_current_object(), client,
			messageContent, recipientNumber)).start()



def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)



def send_email(subject, sender, recipients, text_body, html_body, **kwargs):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = render_template(text_body, **kwargs)
    msg.html = render_template(html_body, **kwargs)
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()



def send_estimate(quoteRequest, job_items, docType, token):
    send_email('Your {}'.format(docType),
               sender=current_app.config['ADMINS'][0],
               recipients=[quoteRequest.email],
               text_body='quoteResponseEmail.txt',
               html_body= 'quoteResponseEmail.html',
               q_request=quoteRequest,
               job_items=job_items, type=docType, token=token)


def create_stripe_customer(email):
	stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
	customer = stripe.Customer.create(email=email)
	return customer


def send_stripe_invoice(stripe_id, job_items):
	stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
	for item in job_items:
		stripe.InvoiceItem.create(
		  amount=item.estimate,
		  currency='usd',
		  customer=stripe_id,
		  description=item.description,
		)
	invoice = stripe.Invoice.create(
	  customer=stripe_id,
	  billing='send_invoice',
	  days_until_due=30,
	)
	



