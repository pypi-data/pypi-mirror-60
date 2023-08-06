from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import base64
from email.mime.multipart import MIMEMultipart

class SendMail():

    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    # If modifying these scopes, delete the file token.pickle.
    def create_credentials(self):
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('gmail', 'v1', credentials=creds)

        return service

    def get_labels(self, service):
        # Call the Gmail API
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
        else:
            print('Labels:')
            for label in labels:
                print(label['name'])

    def CreateMessage(self, address, msgPlain):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Training Completed'
        msg['From'] = address
        msg['To'] = address
        msg.attach(MIMEText(msgPlain, 'plain'))
        #msg.attach(MIMEText(msgHtml, 'html'))
        raw = base64.urlsafe_b64encode(msg.as_bytes())
        raw = raw.decode()
        body = {'raw': raw}
        return body


    def send_msg(self, service, body):
        results = service.users().messages().send(userId='me', body=body, media_body=None, media_mime_type=None).execute()
        return results