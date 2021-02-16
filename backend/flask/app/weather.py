""" get data from openweathermap.org """

from datetime import datetime
from time import sleep
import json

import requests


def get_weather(config):
    """ 
    gets the missing weather data from openweathermap 
    return: json string
    """
    api_key = config['api_key']
    lat = config['lat']
    lon = config['lon']
    # get data
    r = requests.get("https://api.openweathermap.org/data/2.5/weather?&units=metric&appid=" + api_key + "&lat=" + lat + "&lon=" + lon, timeout=20)
    # format data
    r_json = r.json()
    weather_name = r_json['weather'][0]['main']
    weather_icon = r_json['weather'][0]['icon']
    wind_speed = r_json['wind']['speed']
    wind_direction = r_json['wind']['deg']
    # timestamp
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    epoch_time = int(now.strftime('%s'))
    # form dict
    json_dict = {}
    json_dict['weather_name'] = weather_name
    json_dict['weather_icon'] = weather_icon
    json_dict['wind_speed'] = wind_speed
    json_dict['wind_direction'] = wind_direction
    json_dict['timestamp'] = timestamp
    json_dict['epoch_time'] = epoch_time
    # return json string
    weather_json = json.dumps(json_dict)
    return weather_json, timestamp


def handle_weather(config):
    """ sets infinite loop to collect api data """
    weather_json, timestamp = get_weather(config)
    with open('dyn/weather.json', 'w') as f:
        f.write(weather_json)
    print(f'weather data updated: {timestamp}')
