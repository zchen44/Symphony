from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import os
from twilio.rest import Client
from apiclient import errors

class Gmail():
	def __init__(self):
		self.service = self.get_credentials()

	def get_credentials(self):
		# Setup the Gmail API
		SCOPES = [	'https://www.googleapis.com/auth/gmail.readonly',
					'https://www.googleapis.com/auth/gmail.compose',
					'https://www.googleapis.com/auth/gmail.send',
					'https://www.googleapis.com/auth/gmail.insert',
					'https://www.googleapis.com/auth/gmail.metadata'
				]
		store = file.Storage('credentials.json')
		creds = store.get()
		if not creds or creds.invalid:
			flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
			creds = tools.run_flow(flow, store)
		service = build('gmail', 'v1', http=creds.authorize(Http()))
		return service

	def SendMessage(self, user_id, message):
		"""Send an email message.

		Args:
		service: Authorized Gmail API service instance.
		user_id: User's email address. The special value "me"
		can be used to indicate the authenticated user.
		message: Message to be sent.

		Returns:
		Sent Message.
		"""
		try:
			message = (self.service.users().messages().send(userId=user_id, body=message)
					   .execute())
			print('Message Id: %s' % message['id'])
			return message
		except errors.HttpError as error:
			print('An error occurred: %s' % error)


def CreateMessage(sender, to, subject, message_text):
	"""
	Creates an object containing a base64url encoded email object.
	"""
	message = MIMEText(message_text)
	message['to'] = to
	message['from'] = sender
	message['subject'] = subject
	raw_message = base64.urlsafe_b64encode(message.as_bytes())
	raw_message = raw_message.decode()
	return {'raw': raw_message }

def CreateMessageWithAttachment(sender, to, subject, message_text, file_dir,
								filename):
	"""Create a message for an email.

	Args:
	sender: Email address of the sender.
	to: Email address of the receiver.
	subject: The subject of the email message.
	message_text: The text of the email message.
	file_dir: The directory containing the file to be attached.
	filename: The name of the file to be attached.

	Returns:
	An object containing a base64url encoded email object.
	"""
	message = MIMEMultipart()
	message['to'] = to
	message['from'] = sender
	message['subject'] = subject

	msg = MIMEText(message_text)
	message.attach(msg)

	path = os.path.join(file_dir, filename)
	content_type, encoding = mimetypes.guess_type(path)

	if content_type is None or encoding is not None:
		content_type = 'application/octet-stream'
	main_type, sub_type = content_type.split('/', 1)
	if main_type == 'text':
		fp = open(path, 'rb')
		msg = MIMEText(fp.read(), _subtype=sub_type)
		fp.close()
	elif main_type == 'image':
		fp = open(path, 'rb')
		msg = MIMEImage(fp.read(), _subtype=sub_type)
		fp.close()
	elif main_type == 'audio':
		fp = open(path, 'rb')
		msg = MIMEAudio(fp.read(), _subtype=sub_type)
		fp.close()
	else:
		fp = open(path, 'rb')
		msg = MIMEBase(main_type, sub_type)
		msg.set_payload(fp.read())
		fp.close()

	msg.add_header('Content-Disposition', 'attachment', filename=filename)
	message.attach(msg)
	raw_message = base64.urlsafe_b64encode(message.as_bytes())
	raw_message = raw_message.decode()
	return {'raw': raw_message }

def send_via_twilio(message, number):
	account_sid = "AC1bc6be9ede1599e8495a8139e6e1fe1f"
	auth_token = "b0989a2758f7821f653f42d660a0c901"
	sms_client = Client(account_sid, auth_token)
	sms_client.messages.create(
		to = number,
		from_ = "6466812635",
		body = (message.author.name + ": " + message.clean_content) )
