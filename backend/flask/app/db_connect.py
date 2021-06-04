""" handles insert into postgres db """

import psycopg2


def db_connect(config):
    """ returns connection and curser """
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
    return conn, cur


def db_close(conn, cur):
    """ clean close the conn and curser """
    conn.commit()
    cur.close()
    conn.close()


def db_insert(config, json_dict):
    """ make the db insert """
    # read out data dict
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
    sensor_id = json_dict['sensor_id']

    # connect
    conn, cur = db_connect(config)
    # insert aqi
    cur.execute("INSERT INTO aqi \
        (epoch_time, sensor_id, time_stamp, uptime, pm25, pm10, aqi_value, aqi_category) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (epoch_time, sensor_id, time_stamp, uptime, pm25, pm10, aqi_value, aqi_category)
    )
    # insert weather
    cur.execute("INSERT INTO weather \
        (epoch_time, sensor_id, time_stamp, temperature, pressure, humidity, \
        wind_speed, wind_direction, weather_name, weather_icon) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
        (epoch_time, sensor_id, time_stamp, temperature, pressure, humidity, 
        wind_speed, wind_direction, weather_name, weather_icon)
    )

    # close
    db_close(conn, cur)

    return time_stamp
