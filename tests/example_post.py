#!/usr/bin/env python3
""" test script to post data to the ingest route """

import requests
import json
import configparser

# get auth
config_parser = configparser.ConfigParser()
config_parser.read('../backend/flask/config')
user_name = config_parser.get('aqi_monitor', "authUsername")
user_pass = config_parser.get('aqi_monitor', "authPassword")

# example json data as from the esp8266
json_data = {
  "uptime": 1476,
  "temperature": 28.46,
  "pressure": 995.0873,
  "humidity": 10.52051,
  "pm25": 56.5,
  "pm10": 64.4
}

# make the call
response = requests.post("https://data.lpb-air.com/ingest", json=json_data, auth = (user_name, user_pass))

# print result
print(response)
print(response.text)
