-- create aqi table
CREATE TABLE aqi (
    epoch_time INT NOT NULL PRIMARY KEY,
    time_stamp VARCHAR(20) NOT NULL,
    uptime INT NOT NULL,
    pm25 FLOAT4 NOT NULL,
    pm10 FLOAT4 NOT NULL,
    aqi_value FLOAT4 NOT NULL,
    aqi_category VARCHAR(40) NOT NULL
);

-- example aqi insert
INSERT INTO aqi (
    epoch_time,
    time_stamp,
    uptime,
    pm25,
    pm10,
    aqi_value,
    aqi_category
) VALUES (
    1613648178, '2021-02-18 18:36:18', 206728, 20.4, 22.8, 67.0, 'Moderate'
);


-- create weather table
CREATE TABLE weather (
    epoch_time INT NOT NULL PRIMARY KEY,
    time_stamp VARCHAR(20) NOT NULL,
    temperature FLOAT4 NOT NULL,
    pressure FLOAT4 NOT NULL,
    humidity FLOAT4 NOT NULL,
    wind_speed FLOAT4 NOT NULL,
    wind_direction INT2 NOT NULL,
    weather_name VARCHAR(29) NOT NULL,
    weather_icon VARCHAR(3) NOT NULL
);

-- example weather insert
INSERT INTO weather (
    epoch_time,
    time_stamp,
    temperature,
    pressure,
    humidity,
    wind_speed,
    wind_direction,
    weather_name,
    weather_icon
) VALUES (
    1613648178, '2021-02-18 18:36:18', 27.32, 982.41, 
    39.62598, 3.09, 40, 'Clouds', '04n'
);
