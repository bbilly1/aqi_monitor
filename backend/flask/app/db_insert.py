""" handles insert into postgres db """

import psycopg2
import traceback


def db_connect(config, data):
    """ handles the data insert """
    # set config
    db_host = config['db_host']
    db_database = config['db_database']
    db_user = config['db_user']
    db_password = config['db_password']

    # Connect to database
    conn = psycopg2.connect(
        host = db_host,
        database = db_database,
        user = db_user,
        password = db_password
    )

    # Open a cursor to perform database operations
    cur = conn.cursor()
    
    # insert
    time_stamp = db_insert(cur, data)
    
    # finish
    conn.commit()
    cur.close()
    conn.close()
    # print
    return time_stamp


def db_insert(cur, json_dict):
    """ make the db insert """
    # read out data dict
    try:
        uptime = json_dict['uptime']
        temperature = json_dict['temperature']
        pressure = json_dict['pressure']
        humidity = json_dict['humidity']
        pm25 = json_dict['pm25']
        pm10 = json_dict['pm10']
        aqi_value = json_dict['aqi_value']
        aqi_category = json_dict['aqi_category']
        time_stamp = json_dict['timestamp']
        epoch_time = json_dict['epoch_time']
        weather_name = json_dict['weather_name']
        weather_icon = json_dict['weather_icon']
        wind_speed = json_dict['wind_speed']
        wind_direction = json_dict['wind_direction']
    except Exception:
        print('json_dict parsing error')
        print(traceback.format_exc())
        time_stamp = "parse error"
    try:
        # insert aqi
        cur.execute("INSERT INTO aqi \
            (epoch_time, time_stamp, uptime, pm25, pm10, aqi_value, aqi_category) \
            VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (epoch_time, time_stamp, uptime, pm25, pm10, aqi_value, aqi_category))
    except Exception:
        print('aqi INSERT error')
        print(traceback.format_exc())
        time_stamp = "aqi error"
    try:
        # insert weather
        cur.execute("INSERT INTO weather \
            (epoch_time, time_stamp, temperature, pressure, humidity, \
            wind_speed, wind_direction, weather_name, weather_icon) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
            (epoch_time, time_stamp, temperature, pressure, humidity, 
            wind_speed, wind_direction, weather_name, weather_icon)
        )
    except Exception:
        print('weather INSERT error')
        print(traceback.format_exc())
        time_stamp = "weather error"
    return time_stamp
