import os
import hashlib
import hmac
import base64
from db import mongo
from flask import Blueprint, request, session, jsonify
from utils import json_response

auth = Blueprint('auth', __name__)

db = mongo.cx['TrackTrack']
Users = db['Users']


@auth.route('/register', methods=["POST"])
def registration():
	body = request.get_json()
	if 'login' not in body or type(body['login']) is not str or 'password' not in body or type(body['password']) is not str:
		return json_response({"message": "BAD_PARAMS"}, 400)
	user = Users.find_one({"login": body['login']})
	if user:
		return json_response({"message": "USER_ALREADY_EXISTS"}, 400)

	salt = os.urandom(16)
	pw_hash = hashlib.pbkdf2_hmac('sha256', body['password'].encode(), salt, 100000)
	
	salt_b64 = base64.b64encode(salt).decode('utf-8')
	pw_hash_b64 = base64.b64encode(pw_hash).decode('utf-8')
	
	Users.insert_one({"login": body['login'], "salt": salt_b64, "hash": pw_hash_b64})
	return json_response()

# @auth.route('/login', methods=["POST"])
# def login():
# 	body = request.get_json()
# 	if 'login' not in body or body['login'] is not str or 'password' not in body or body['password'] is not str:
# 		return jsonify({"status": 400, "message": "BAD_PARAMS"})
# 	user = Users.find_one({"login": body['login']})
# 	if not user:
# 		return jsonify({"status": 400, "message": "USER_NOT_EXISTS"})
# 	stored_salt = base64.b64decode(sole)
# 	stored_hashed_password = base64.b64decode(pwhash)

# 	# Recompute the hash for the provided password and stored salt
# 	new_hashed_password = hashlib.pbkdf2_hmac(
# 		'sha256', 
# 		password.encode(), 
# 		stored_salt, 
# 		100000  # Use the same number of iterations as during registration
# 	)

# 	# Compare the new hash with the stored hash
# 	if new_hashed_password == stored_hashed_password:
# 		print("Matching")
# 	else:
# 		print("Not matching")
# 	return new_hashed_password == stored_hashed_password

