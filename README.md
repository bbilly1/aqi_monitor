# AQI sensor project

This is a place to show off what went into building my AQI measuring station currently publishing to:

[lpb-air.com](lpb-air.com)

This is under constant development. The main purpose is educational.

The webserver is a simple VPS, provisioned with docker-compose.yml.

## aqi_monitor
*aqi_monitor.ino* is the arduino script running on the **nodeMCU ESP8266** microcontroller. The microcontroller posts data to the flask backend on a regular interval.
Connected to that is:  
* SDS011: pm2.5 and pm10 sensor from Nova Fitness.
* BME280: Pressure Humidity Temperature Sensor Module.

## backend
A [flask](https://pypi.org/project/Flask/) based application that takes the data from the ESP8266 for processing and storage.  
[Postgres](https://www.postgresql.org/) handles the storage of the measurements. The data is split up into two different tables, one for aqi related data and one for the weather data.  
Python interacts with Postgres with the help of the [psycopg](https://www.psycopg.org/) library.  
The flask app is recreating the graphs to visualize the aqi, PM 2.5 and PM 10 values on an interval. Aggregating is done with the [Pandas](https://pandas.pydata.org/) Python library and the graphs are created with [matplotlib](https://matplotlib.org/).  
The backend runs on a separate subdomain so it could easily be scaled horizontaly onto a separate server in the future.

## frontend
A simple web site that gets AQI values from the backend to publish it nicely to see. Mostly build with HTML/CSS/JS and a little bit of PHP.  
New data is pulled from the backend on a interval with JavaScript and XMLHttpRequest library.  
The Lightbox to take a closer look at the graphs is curtesy of [Lokesh Dhakar](https://github.com/lokesh/lightbox2).
