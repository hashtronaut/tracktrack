import re
import json
import smtplib
import os
from flask import make_response
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bson import ObjectId


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



def validate_password(password):
    return re.match(r'^[A-Z]+[a-z]+[\W_]+.{6,23}$', password)

def validate_login(login):
    return re.match(r'^[a-zA-Z0-9]{3,12}$', login)

def validate_name(name):
    if type(name) is not str:
        return False
    return re.match('[A-Za-zА-Яа-я]?', name)

def json_response(data=None, status=200):
    headers = {'Content-Type':'application/json'}
    if data is None:
        return make_response('', status, headers)
    body = toJson.encode(data)
    return make_response(body, status, headers)
                        
if __name__ == '__main__':
    print(str(validate_password("Fl@shinthenight")))

