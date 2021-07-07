""" handle db connections """

import json
from datetime import datetime

import psycopg2
import requests

from src.helper import get_config


class DatabaseConnect:
    """ handle db """

    CONFIG = get_config()

    def __init__(self):
        self.conn, self.cur = self.db_connect()

    def db_connect(self):
        """ returns connection and curser """
        # Connect to database
        conn = psycopg2.connect(
            host=self.CONFIG['postgres']['db_host'],
            database=self.CONFIG['postgres']['db_database'],
            user=self.CONFIG['postgres']['db_user'],
            password=self.CONFIG['postgres']['db_password']
        )
        # Open a cursor to perform database operations
        cur = conn.cursor()
        return conn, cur

    def db_execute(self, query):
        """ run a query """
        if isinstance(query, str):
            self.cur.execute(
                query
            )
            rows = self.cur.fetchall()
        elif isinstance(query, tuple):
            self.cur.execute(
                query[0], query[1]
            )
            rows = False

        return rows

    def db_close(self):
        """ clean close the conn and curser """
        self.conn.commit()
        self.cur.close()
        self.conn.close()


class IngestLine:
    """ handle data input from monitor """

    def __init__(self, data):
        self.aqi_query = None
        self.weather_query = None
        self.input_json = data
        self.add_aqi()
        self.add_timestamp()
        self.add_weather()
        self.add_query()

    def add_aqi(self):
        """ add aqi_value and aqi_category keys from pm2.5 value """

        aqi_breakpoints = [
            ('Good', 0, 12.0, 0, 50),
            ('Moderate', 12.1, 35.4, 51, 100),
            ('Unhealthy for Sensitive Groups', 35.5, 55.4, 101, 150),
            ('Unhealthy', 55.5, 150.4, 151, 200),
            ('Very Unhealthy', 150.5, 250.4, 201, 300),
            ('Hazardous', 250.5, 500.4, 301, 500),
        ]

        pm25 = self.input_json['pm25']
        for i in aqi_breakpoints:
            aqi_category, p_low, p_high, a_low, a_high = i
            if p_low < pm25 < p_high:
                # found it
                break

        aqi = (a_high - a_low) / (p_high - p_low) * (pm25 - p_low) + a_low

        aqi_dict = {
            'aqi_value': round(aqi),
            'aqi_category': aqi_category
        }

        self.input_json.update(aqi_dict)

    def add_timestamp(self):
        """ add timestamp to dict """
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        epoch_time = int(now.strftime('%s'))

        time_stamp_dict = {
            'time_stamp': timestamp,
            'epoch_time': epoch_time
        }

        self.input_json.update(time_stamp_dict)

    def add_weather(self):
        """ add weather data to dict """
        weather = Weather().last_weather
        self.input_json.update(weather)

    def add_query(self):
        """ add aqi and weather query to self """
        aqi_keys = (
            'epoch_time', 'sensor_id', 'time_stamp', 'uptime',
            'pm25', 'pm10', 'aqi_value', 'aqi_category'
        )
        aqi_query = self.build_query(aqi_keys, 'aqi')
        weather_keys = (
            'epoch_time', 'sensor_id', 'time_stamp', 'temperature',
            'pressure', 'humidity', 'wind_speed', 'wind_direction',
            'weather_name', 'weather_icon'
        )
        weather_query = self.build_query(weather_keys, 'weather')
        self.aqi_query = aqi_query
        self.weather_query = weather_query

    def build_query(self, keys, table):
        """ stitch query together for psycopg2 """
        keys_str = ', '.join(keys)
        valid = ', '.join(['%s' for i in keys])
        values = tuple(self.input_json[i] for i in keys)

        query = (f'INSERT INTO {table} ({keys_str}) VALUES ({valid});', values)

        return query


class Weather:
    """ handle weather lookup from API """

    CONFIG = get_config()

    def __init__(self):
        now = datetime.now()
        self.epoch_time = int(now.strftime('%s'))
        self.last_weather = self.get_weather()

    def get_weather(self):
        """ get weather from disk or api if too old """
        try:
            last_dict = self.get_cache()
        except FileNotFoundError:
            # create for first time
            last_dict = self.get_openweather()
        last_epoch = last_dict['epoch_time']

        if self.epoch_time - last_epoch > 10 * 60:
            print('get new weather data')
            weather = self.get_openweather()
        else:
            print('reuse weather data')
            weather = last_dict

        del weather['epoch_time']

        return weather

    def get_openweather(self):
        """ get missing weatherdata from openweathermap api """
        api_key = self.CONFIG['openweathermap']['api_key']
        lat = self.CONFIG['openweathermap']['lat']
        lon = self.CONFIG['openweathermap']['lon']

        url = ('https://api.openweathermap.org/data/2.5/weather' +
               f'?&units=metric&appid={api_key}&lat={lat}&lon={lon}')
        resp = requests.get(url, timeout=20).json()
        weather = {
            'weather_name': resp['weather'][0]['main'],
            'weather_icon': resp['weather'][0]['icon'],
            'wind_speed': resp['wind']['speed'],
            'wind_direction': resp['wind']['deg'],
            'epoch_time': self.epoch_time
        }
        self.write_cache(weather)

        return weather

    @staticmethod
    def get_cache():
        """ get last stored dict """
        with open('static/dyn/weather.json', 'r') as f:
            last = f.read()

        last_dict = json.loads(last)
        return last_dict

    @staticmethod
    def write_cache(weather):
        """ update last stored value """
        weather_str = json.dumps(weather)
        with open('static/dyn/weather.json', 'w') as f:
            f.write(weather_str)


def get_current():
    """ get last values from db """

    db_handler = DatabaseConnect()
    aqi = db_handler.db_execute(
        'SELECT time_stamp, aqi_value, aqi_category \
        FROM aqi ORDER BY epoch_time DESC LIMIT 1;'
    )
    weather = db_handler.db_execute(
        'SELECT temperature, pressure, humidity, \
        wind_speed, weather_name, weather_icon \
        FROM weather ORDER BY epoch_time DESC LIMIT 1;'
    )
    db_handler.db_close()

    json_dict = {
        "temperature": weather[0][0],
        "pressure": weather[0][1],
        "humidity": weather[0][2],
        "weather_name": weather[0][4],
        "weather_icon": weather[0][5],
        "timestamp": aqi[0][0],
        "aqi_value": aqi[0][1],
        "aqi_category": aqi[0][2],
        "wind_speed": weather[0][3]
    }
    json_data = json.dumps(json_dict)
    return json_data


def insert_data(data):
    """ called from ingest route to make the db insert """

    ingest = IngestLine(data)

    db_handler = DatabaseConnect()
    _ = db_handler.db_execute(ingest.aqi_query)
    _ = db_handler.db_execute(ingest.weather_query)
    db_handler.db_close()
