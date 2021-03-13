-- get data for time span from now
-- where epoch_time value is used for filtering
SELECT
    epoch_time, aqi_value 
    FROM aqi 
    WHERE epoch_time > 1613975843 
    ORDER BY epoch_time DESC;


-- get data from yesterday
SELECT
    epoch_time, aqi_value
    FROM aqi
    WHERE epoch_time > 1613926800
    AND epoch_time < 1614013200
    ORDER BY epoch_time DESC
    LIMIT 30 * 24;


-- last 7 days
SELECT 
    epoch_time, aqi_value 
    FROM aqi 
    WHERE epoch_time > 1613494800 
    AND epoch_time < 1614099600 
    ORDER BY epoch_time DESC 
    LIMIT 30 * 24 * 7;


-- last 48h of pm2.5 and pm10 values
SELECT 
    epoch_time, pm25, pm10 
    FROM aqi 
    WHERE epoch_time < 1614963600 
    AND epoch_time > 1614790800 
    ORDER BY epoch_time DESC 
    LIMIT 30 * 48;
