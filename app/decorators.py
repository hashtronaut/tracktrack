from functools import wraps
from flask import Response, g, request
from utils import json_response
from db import mongo


db = mongo.cx['TrackTrack']
Session = db['Session']

def check_auth(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.header['Authorization']
        session = Session.find_one({"token": token})
        if not session:
            return json_response({"message": "unauthorized"}, 401)
        return func(*args, **kwargs)
    return decorated