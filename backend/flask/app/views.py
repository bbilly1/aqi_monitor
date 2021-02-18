import configparser
import json

from flask_cors import CORS
from flask import request
from flask_httpauth import HTTPBasicAuth
from apscheduler.schedulers.background import BackgroundScheduler


from app import app
from app import aqi_parser
from app import weather
from app import db_insert

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
    config["api_key"] = config_parser.get('openweathermap', "api_key")
    config["lat"] = config_parser.get('openweathermap', "lat")
    config["lon"] = config_parser.get('openweathermap', "lon")
    # db
    config["db_host"] = config_parser.get('postgres', "db_host")
    config["db_database"] = config_parser.get('postgres', "db_database")
    config["db_user"] = config_parser.get('postgres', "db_user")
    config["db_password"] = config_parser.get('postgres', "db_password")
    return config


# start up
config = get_config()
weather.handle_weather(config)
# build username / pw dict for basic auth
USER_DATA = {}
USER_DATA[config['authUsername']] = config['authPassword']


# start scheduler
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    weather.handle_weather, args=[config], trigger="interval", name='weather_api', seconds=900
)


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
        # populate data dict
        json_dict = aqi_parser.input_process(data)
        # save to db
        time_stamp = db_insert.db_connect(config, json_dict)
        print(f'db insert done at {time_stamp}')
        # save to webserver
        data = json.dumps(json_dict)
        with open('dyn/air.json', 'w') as f:
            f.write(data)
        print(data)
    return 'ingest'


# output
@app.route('/')
def home():
    try:
        with open('dyn/air.json', 'r') as f:
            data = f.read()
    except FileNotFoundError:
        # will get regeneratod on next run
        data = '{}'
    return data
