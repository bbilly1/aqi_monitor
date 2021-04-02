import configparser
import json

from flask import request
from flask_httpauth import HTTPBasicAuth
from apscheduler.schedulers.background import BackgroundScheduler


from app import app
from app import aqi_parser
from app import weather
from app import graph
from app import graph_pm
from app import table_export
from app import graph_monthly
from app.db_connect import db_insert


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
auth = HTTPBasicAuth()
config = get_config()
weather.handle_weather(config)
graph.create_current(config)
graph_pm.rebuild_pm_bar(config)
graph.rebuild_3days(config)
graph.rebuild_7days(config)
graph_pm.rebuild_hour_bar(config)
table_export.rebuild_table(config)
graph_monthly.create_monthly(config)

# build username / pw dict for basic auth
USER_DATA = {}
USER_DATA[config['authUsername']] = config['authPassword']


# start scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    weather.handle_weather, args=[config], trigger="interval", name='weather_api', seconds=900
)
scheduler.add_job(
    graph.create_current, args=[config], trigger="cron", minute='*/5', name='current_graph'
)
scheduler.add_job(
    graph.rebuild_3days, args=[config], trigger="cron", day='*', hour='1', minute='1', name='3_days'
)
scheduler.add_job(
    graph.rebuild_7days, args=[config], trigger="cron", day='*', hour='1', minute='2', name='7_days'
)
scheduler.add_job(
    graph_pm.rebuild_pm_bar, args=[config], trigger="cron", day='*', hour='1', minute='3', name='pm_bar'
)
scheduler.add_job(
    graph_pm.rebuild_hour_bar, args=[config], trigger="cron", day='*', hour='1', minute='4', name='hour_bar'
)
scheduler.add_job(
    table_export.rebuild_table, args=[config], trigger="cron", day='*', hour='1', minute='6', name='rebuild_table'
)
scheduler.add_job(
    graph_monthly.create_monthly, args=[config], trigger="cron", day='*', hour='1', minute='7', name='create_monthly'
)
scheduler.start()


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
        json_dict, error_found = aqi_parser.input_process(data)
        if error_found:
            print('pm25 read failed')
            print(json_dict)
        else:
            # save to db
            time_stamp = db_insert(config, json_dict)
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
