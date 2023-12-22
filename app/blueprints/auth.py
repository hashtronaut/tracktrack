import os 
import secrets
import hashlib
import hmac
import base64
import uuid
from models.User import User
from db import mongo
from flask import Blueprint, request, session, make_response
from utils import json_response, validate_name, validate_password, validate_login

auth = Blueprint('auth', __name__)

db = mongo.cx['TrackTrack']
Users = db['Users']
Session = db['Session']

@auth.route('/register', methods=["POST"])
def registration():
	body = request.get_json()

	if 'login' not in body or type(body['login']) is not str or 'password' not in body or type(body['password']) is not str\
		or 'name' not in body or type(body['name']) is not str:
		return json_response({"message": "BAD_ARGS"}, 400)
	if not validate_login(body['login']):
		return json_response({"message": "BAD_LOGIN"}, 400)
	if not validate_password(body['password']):
		return json_response({"message": "BAD_PASSWORD"}, 400)
	if not validate_name(body['name']):
		return json_response({"message": "BAD_NAME"}, 400)

	user = User()
	response = user.register(body['login'], body['password'], body['name'])
	
	if response["success"]:
		return json_response({"message": response['message']})	
	return json_response({"message": response['message']}, 400)

@auth.route('/login', methods=["POST"])
def login():
	body = request.get_json()
	if 'login' not in body or type(body['login']) is not str or 'password' not in body or type(body['password']) is not str:
		return json_response({"message": "BAD_PARAMS"}, 400)
	user = Users.find_one({"login": body['login']})
	if not user:
		return json_response({"message": "USER_NOT_EXISTS"}, 400)
	#return json_response({"user": user})
	stored_salt = base64.b64decode(user['salt'])
	stored_hashed_password = base64.b64decode(user['hash'])

	# Recompute the hash for the provided password and stored salt
	new_hashed_password = hashlib.pbkdf2_hmac(
		'sha256', 
		body['password'].encode(), 
		stored_salt, 
		100000  # Use the same number of iterations as during registration
	)

	# Compare the new hash with the stored hash
	if new_hashed_password == stored_hashed_password:
		token = secrets.token_urlsafe(30*3//4)
		response = make_response()
		response.headers['Authorization'] = token
		Session.update_one({"userID": user['userID']}, {"$set": {"token": token, "expiry": False}}, upsert=True)
		return response
	else:
		return json_response({"message": "WRONG_PASSWORD"})

