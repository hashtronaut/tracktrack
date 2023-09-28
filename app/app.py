#!/bin/env python3
import os
from flask import Flask, Blueprint
from dotenv import load_dotenv
from db import mongo

# load the environment variables from the .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")  # needed for cryptography(especially cookie sessions)
#app.permanent_session_lifetime = timedelta(days=30)


app.config['MONGO_URI'] = os.environ.get("MONGO_CONNECTION_STRING")
#app.config['MONGO_URI'] = "mongodb+srv://hashtronaut:sgUIEV7ezdjP5MbU@cluster0.ssrditb.mongodb.net/?retryWrites=true&w=majority"
mongo.init_app(app) # initialize here!



mainBp = Blueprint("api", __name__, url_prefix="/api")


from blueprints.auth import auth
mainBp.register_blueprint(auth)


@mainBp.route('/', methods=["GET"])
def index():
    return "Flask is UP!"


app.register_blueprint(mainBp)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7000)

