#Sanele Mpangalala
#Thinkst Tech Evalution

from flask import Flask, request, render_template
from flask_celery_integration import make_celery
from tasks import *

import dns.resolver
import socket
import smtplib
#creating a Flask app
app = Flask(__name__)
app.config['CELERY_BROKER_URL']= "redis://localhost:6379/0"
app.config['CELERY_BACKEND'] = "redis://localhost/0"


#app.debug = True

#routing the app 
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "POST":
	    #The data from POST comes in the format: to|subject|message
        data = request.form["data"]
		#get 'to'
        to = data.split("|")[0]
		
		#get 'subject'
        subject = data.split("|")[1]
		
		#get 'message'
        message = data.split("|")[2]
        
		result = ""  #is email sent or not?
		#If the tyhe email address is valid, send email
        if(validate_email_address(to)):
            send_mail.delay("aynstyn@gmail.com",to, subject, message) #I'm using my Gmail account to send email
            result = "Email has been sent"
        else:
            result = "Invalid email address"
        return result
    return render_template("index.html")
	
def validate_email_address(email):
    #To start verification, we need to get the mail exchanger (MX) record for the target domain
    target_domain = email.split('@')[1]
    records = dns.resolver.query(target_domain, 'MX')
    mx_record = str(records[0].exchange)

    #local server hostname
    host = socket.gethostname()

    #Setting the SMTP library
    server = smtplib.SMTP()
    server.set_debuglevel(0)

    #starting the SMTP communication between host and the target domain
    server.connect(mx_record)
    server.helo(host)
    server.mail('aynstyn@gmail.com')
    code, message = server.rcpt(str(email)) #code=250 for a successful communication
    server.quit()
	
    valid = ""
    # Assume 250 as Success
    if code == 250:
        valid = True
    else:
        valid = False
		
    return valid
if __name__ == "__main__":
    app.run()