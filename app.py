import os
from googleapiclient.discovery import build
import requests
from flask import Flask, redirect, request, url_for, render_template, jsonify
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build_from_document
import openai
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64



app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  
CLIENT_SECRETS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
REDIRECT_URI = 'http://localhost:5007/callback'

flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=SCOPES,
    redirect_uri=REDIRECT_URI
)

@app.route('/')
def index():
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return redirect(authorization_url)


@app.route('/callback')
#def callback():
  #  print('we are in cb')

    #flow.fetch_token(authorization_response=request.url)
    #print('fetch done')
    #if not flow.credentials:
      #  return "Error: Missing access token", 400
    #credentials = flow.credentials

    #session = requests.Session()
    #token = credentials.token

    #service = build('gmail', 'v1', credentials=credentials)
    #results = service.users().messages().list(userId='me').execute()
    #messages = results.get('messages', [])

    #output = []
    #for message in messages:
     #   msg = service.users().messages().get(userId='me', id=message['id']).execute()
        
def callback():
    try:
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        service = build('gmail', 'v1', credentials=credentials)
        results = service.users().messages().list(userId='me').execute()
        messages = results.get('messages', [])
        
        emails = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            snippet = msg['snippet']
            emails.append(snippet)

        return render_template('dashboard.html', emails=emails)
    
    except Exception as e:
        app.logger.error(f"Error in callback: {e}")
        return "Internal Server Error", 500

openai.api_key = 'sk-proj-kQ6cs0kxxEa1bMkkojC5T3BlbkFJWTcHUL6hMx9T85vAC0HV'
api_endpoint = 'https://api.openai.com/v1/engines/davinci-codex/completions'


@app.route('/generate_response', methods=['POST'])
def generate_response():
    email_content = request.json['email_content']
    response = generate_email_response(email_content)
    return jsonify({'response': response})

@app.route('/send_email', methods=['POST'])
def send_email():
    try:
        credentials = flow.credentials
        service = build('gmail', 'v1', credentials=credentials)

        data = request.json
        to = data['to']
        subject = data['subject']
        body = data['body']

        message = create_message(to, subject, body)
        send_message(service, 'me', message)

        return jsonify({'status': 'Email sent successfully!'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_message(to, subject, body):
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}

def send_message(service, sender, message):
    try:
        message = service.users().messages().send(userId=sender, body=message).execute()
        print('Message Id: %s' % message['id'])
        return message
    except Exception as e:
        print('An error occurred: %s' % e)
        raise

def generate_email_response(email_content):
    try:
        # Define the prompt for GPT-3
        prompt = f"Generate a email response to the following email content:\n\n{email_content}"
        
        response = openai.ChatCompletion.create(
            model="gpt-4-0125-preview", 
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,  
            temperature=0.7  
        )
        email_response = response.choices[0].text.strip()
        return email_response
    
    except Exception as e:
        return f"Error generating response: {e}"

    response = requests.post(api_endpoint, headers=headers, json=data)

if __name__ == '__main__':
    app.run('localhost', 5007, debug=True)
