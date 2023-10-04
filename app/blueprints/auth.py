import os 
import secrets
import hashlib
import hmac
import base64
import uuid
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
	# keys = ['login', 'password', 'name']
	# for key in body.keys():
	# 	if key not in keys:
	# 		return json_response({"message": "INVALID_ARGS"}, 400)
	# 	#setting name of imported validation function by the key in body
	# 	func_name = f'validate_{key}'
	# 	#setting name of function to func
	# 	func = globals()[func_name]
	# 	if type(body[key]) is not str or not func(body[key]):
	# 		return json_response({"message": f'INVALID_{key.upper()}'}, 400)

	if 'login' not in body or type(body['login']) is not str or 'password' not in body or type(body['password']) is not str\
		or 'name' not in body or type(body['name']) is not str:
		return json_response({"message": "BAD_ARGS"})
	if not validate_login(body['login']):
		return json_response({"message": "BAD_LOGIN"}, 400)
	if not validate_password(body['password']):
		return json_response({"message": "BAD_PASSWORD"}, 400)
	if not validate_name(body['name']):
		return json_response({"message": "BAD_NAME"}, 400)

	user = Users.find_one({"login": body['login']})
	if user:
		return json_response({"message": "USER_ALREADY_EXISTS"}, 400)

	salt = os.urandom(16)
	pw_hash = hashlib.pbkdf2_hmac('sha256', body['password'].encode(), salt, 100000)
	
	salt_b64 = base64.b64encode(salt).decode('utf-8')
	pw_hash_b64 = base64.b64encode(pw_hash).decode('utf-8')
	userID = str(uuid.uuid4())
	Users.insert_one({"userID": userID, "login": body['login'], "salt": salt_b64, "hash": pw_hash_b64})
	return json_response()

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

