#Sanele Mpangalala
#Thinkst Tech Evalution

from celery import Celery
from flask import Flask
from flask_celery_integration import make_celery
import smtplib
import httplib2
import os
import oauth2client
from oauth2client import client, tools
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apiclient import errors, discovery

celery = Celery('tasks', broker = "redis://localhost:6379/0") #creating a Celery app

#creating a salary task to send email
@celery.task(name='tasks.send_mail')
def send_mail(sender, to, subject, body):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    message = create_message(sender, to, subject, body)
    send_message(service, "me", message)
	
	#This uses the Google API for emails
	#https://developers.google.com/gmail/api/guides/sending
def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'gmail-python-email-send.json')
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text.encode('utf-8'), 'plain', 'utf-8')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
