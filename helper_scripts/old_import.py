#!/usr/bin/env python3
"""
reading out old log files to import into postgres 

example log_line json dict:
{"timestamp": "2020-03-06 12:16:06", "timeepoch": 1583496966, 
"aqi_value": 86, "aqi_category": "Moderate", "pm25": 29}

example insert_line for postgres:
INSERT INTO aqi (
    epoch_time,
    time_stamp,
    uptime,
    pm25,
    pm10,
    aqi_value,
    aqi_category
) VALUES (1613648178, '2021-02-18 18:36:18', 206728, 20.4, 22.8, 67.0, 'Moderate');

"""

import os
import json
import numpy as np
from datetime import datetime


home = os.path.expanduser("~")
root_path = "sync/system/vps/vps2/logs/aqi/"

log_path = os.path.join(home, root_path)
log_files = sorted(os.listdir(root_path))

columns = "epoch_time, time_stamp, uptime, pm25, pm10, aqi_value, aqi_category"

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

insert_lines = []

# loop through files
for log_file in log_files:
    log_file_path = os.path.join(root_path, log_file)
    with open(log_file_path, 'r') as f:
        log_lines = f.readlines()
    # loop through lines in file
    for log_line in log_lines:
        log_line_dict = json.loads(log_line)
        timeepoch = log_line_dict['timeepoch']
        pm25 = log_line_dict['pm25']
        time_stamp = datetime.fromtimestamp(timeepoch).strftime('%Y-%m-%d %H:%M:%S')
        aqi, aqi_category = get_AQI(pm25)
        values = timeepoch, time_stamp, 0, pm25, 0, aqi, aqi_category
        insert_line = f'INSERT INTO aqi ({columns}) VALUES {values};\n'
        insert_lines.append(insert_line)


# write to file
with open('insert.sql', 'w') as f:
    f.writelines(insert_lines)
