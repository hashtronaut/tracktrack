import re
import json
import smtplib
import os
from flask import make_response
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class ModuleException(Exception):
    def __init__(self, error_data):
        self.error_data = error_data
        super().__init__(self.error_data.get("message", ""))


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):  # Convert ObjectId to string representation
            return str(o)
        return json.JSONEncoder.default(self, o)

toJson = JSONEncoder()


def validate_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

def validate_name(name):
    return re.match('[A-Za-zА-Яа-я]{2,25}( [A-Za-zА-Яа-я]{2,25})?', name)

def json_response(data=None, status=200):
    headers = {'Content-Type':'application/json'}
    if data is None:
        return make_response('', status, headers)
    body = toJson.encode(data)
    return make_response(body, status, headers)
                        

def send_mail(recipient, subject, message, data=None):
    sendTelegramCode(recipient, subject, message)
    sender = os.environ.get("SENDER")
    password = os.environ.get("PASSWORD")
    # password = "flash1nthen1ght"
    # sender = "astrofixed@om-webmasters.org"
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()  # start TLS for security
    s.login(sender, password)
    message = message.encode('utf-8')

    msg = MIMEMultipart()   # create message object
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain', 'utf-8'))    # attach message text to message object

    s.sendmail(sender, recipient, msg.as_string())
    s.quit()


def sendTelegramCode(email, subject, message):
    import requests 
    import os
    token = os.environ.get("BOT_TOKEN")
    message = f'{email}\n{subject}\n\n{message}'
    if not token:
        print(message)
        return
    #chat_id = -1001888581797
    chat_id = os.environ.get('CHAT_ID')

    send_message = requests.get(f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}')


