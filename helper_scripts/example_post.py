#!/usr/bin/env python3
"""
script to post data to the ingest route with simulated data for testing

"""
import json
import requests


def get_config():
    """ read config file """
    config_path = 'flask_aqi/config.json'

    with open(config_path, 'r') as config_file:
        data = config_file.read()

    config = json.loads(data)

    return config

# get auth

CONFIG = get_config()
user_name = CONFIG['aqi_monitor']['authUsername']
user_pass = CONFIG['aqi_monitor']['authPassword']


# example json data as from the esp8266
example_data = '{"uptime":33,"temperature":35.36,"pressure":970.9545,"humidity":41.44336,"pm25":4.5,"pm10":6.2,"sensor_id":1}'


# make the call
response = requests.post("http://localhost:5000/data/in", json=example_data, auth = (user_name, user_pass))

# print result
print(response)
print(response.text)
