import configparser

from flask_cors import CORS
from flask import request
from flask_httpauth import HTTPBasicAuth

from app import app
from app import aqi_parser

cors = CORS(app, resources={r"/": {"origins": "*"}})
auth = HTTPBasicAuth()


def get_config():
    """ read out config file """
    # parse
    config_parser = configparser.ConfigParser()
    config_parser.read('config')
    # build dict
    config = {}
    config["authUsername"] = config_parser.get('aqi_monitor', "authUsername")
    config["authPassword"] = config_parser.get('aqi_monitor', "authPassword")
    return config


config = get_config()


# build username / pw dict for basic auth
USER_DATA = {}
USER_DATA[config['authUsername']] = config['authPassword']


@auth.verify_password
def verify(username, password):
    if not (username and password):
        return False
    return USER_DATA.get(username) == password


# ingest
@app.route('/ingest', methods=['POST'])
@auth.login_required
def ingest():
    data = request.json
    if data:
        data = aqi_parser.input_process(data)
        with open('dyn/values.json', 'w') as f:
            f.write(data)
        print(data)
    return 'ingest'


# output
@app.route('/')
def home():
    try:
        with open('dyn/values.json', 'r') as f:
            data = f.read()
    except FileNotFoundError:
        # will get regeneratod on next run
        data = '{}'
    return data
