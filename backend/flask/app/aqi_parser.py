import json
from datetime import datetime
import numpy as np


def input_process(data):
    """ 
    parsing aqi post data and combine it with weather data
    return: dict of combined values
    """
    # get weather data
    try:
        with open('dyn/weather.json', 'r') as f:
            weather_data = f.read()
        weather_data_json = json.loads(weather_data)
        del weather_data_json['timestamp']
        del weather_data_json['epoch_time']
    except FileNotFoundError:
        # will get recreated on next run
        weather_data_json = {}
    # parse aqi data
    json_dict = data
    pm25 = json_dict['pm25']
    aqi, aqi_category = get_AQI(pm25)
    json_dict['aqi_value'] = float(aqi)
    json_dict['aqi_category'] = aqi_category
    # set timestamp
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    epoch_time = int(now.strftime('%s'))
    json_dict['timestamp'] = timestamp
    json_dict['epoch_time'] = epoch_time
    # combine the two and return
    json_dict.update(weather_data_json)
    return json_dict


def get_AQI(pm25):
    """ takes the pm2.5 value and returns AQI and AQI category """
    if pm25 <= 12:
        aqi = (pm25 / 12) * 50
        aqi_category = "Good"
    elif pm25 > 12 and pm25 <= 35.4:
        perc = (pm25 - 12) / (35.4 - 12)
        aqi = (100 - 50) * perc + 50
        aqi_category = "Moderate"
    elif pm25 > 35.4 and pm25 <= 55.4:
        perc = (pm25 - 35.4) / (55.4 - 35.4)
        aqi = (150 - 100) * perc + 100
        aqi_category = "Unhealthy for Sensitive Groups"
    elif pm25 > 55.4 and pm25 <= 150.4:
        perc = (pm25 - 55.4) / (150.4 - 55.4)
        aqi = (200 - 150) * perc + 150
        aqi_category = "Unhealthy"
    elif pm25 > 150.4 and pm25 <= 199.9:
        perc = (pm25 - 150.4) / (199.9 - 150.4)
        aqi = (250 - 200) * perc + 200
        aqi_category = "Very Unhealthy"
    elif pm25 > 199.9 and pm25 <= 250.4:
        perc = (pm25 - 199.9) / (250.4 - 199.9)
        aqi = (300 - 250) * perc + 250
        aqi_category = "Very Unhealthy"
    elif pm25 > 250.4 and pm25 <= 299.9:
        perc = (pm25 - 250.4) / (299.9 - 250.4)
        aqi = (350 - 300) * perc + 300
        aqi_category = "Hazardous"
    elif pm25 > 299.9 and pm25 <= 350.4:
        perc = (pm25 - 299.9) / (350.4 - 299.9)
        aqi = (400 - 350) * perc + 350
        aqi_category = "Hazardous"
    elif pm25 > 350.4 and pm25 <= 424.6:
        perc = (pm25 - 350.4) / (424.6 - 350.4)
        aqi = (450 - 400) * perc + 400
        aqi_category = "Hazardous"
    elif pm25 > 424.6 and pm25 <= 500.4:
        perc = (pm25 - 424.6) / (500.4 - 424.6)
        aqi = (500 - 450) * perc + 450
        aqi_category = "Hazardous"
    elif pm25 > 500.4:
        aqi = pm25
        aqi_category = "Hazardous"
    aqi = np.round_(int(aqi), decimals=0, out=None)
    return aqi, aqi_category
