import configparser

from flask_cors import CORS
from flask import request
from flask_httpauth import HTTPBasicAuth
from apscheduler.schedulers.background import BackgroundScheduler


from app import app
from app import aqi_parser
from app import weather

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
    return config


config = get_config()


# build username / pw dict for basic auth
USER_DATA = {}
USER_DATA[config['authUsername']] = config['authPassword']


# start scheduler
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    weather.handle_weather, args=[config], trigger="interval", name='weather_api', seconds=300
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
        data = aqi_parser.input_process(data)
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
