from app import create_app, db
from app.models import QuoteRequests, User, JobData, Customer

app = create_app()

@app.shell_context_processor
def make_shell_context():
	return { 
	'db' : db,
	'QuoteRequests' : QuoteRequests,
	'User' : User,
	'JobData' : JobData,
	'customer' : Customer
	}