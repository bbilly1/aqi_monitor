document.addEventListener("DOMContentLoaded", startInterval);


var colorConfig = 
{
    // green
    'Good': [
        "#85a762", "#dbe4d1",
        "invert(66%) sepia(11%) saturate(1318%) hue-rotate(47deg) brightness(92%) contrast(86%)"], 
    // yellow
    'Moderate': [
        "#d4b93c", "#f9f0c7",
        "invert(79%) sepia(5%) saturate(4660%) hue-rotate(9deg) brightness(89%) contrast(103%)"], 
    // orange
    'Unhealthy for Sensitive Groups': [
        "#e96843", "#f8d0c8",
        "invert(61%) sepia(93%) saturate(3252%) hue-rotate(333deg) brightness(95%) contrast(91%)"],
    // red
    'Unhealthy': [
        "#d03f3b", "#f1c5c4",
        "invert(39%) sepia(16%) saturate(2264%) hue-rotate(314deg) brightness(97%) contrast(110%)"],
    // pink
    'Very Unhealthy': [
        "#be4173", "#e9c9d6",
        "invert(45%) sepia(32%) saturate(3238%) hue-rotate(308deg) brightness(77%) contrast(90%)"],
    // violet
    'Hazardous': [
        "#714261", "#d7c6d0",
        "invert(31%) sepia(8%) saturate(2659%) hue-rotate(268deg) brightness(91%) contrast(88%)"]
}


function startInterval() {
    refreshAqiValues();
    setInterval("refreshAqiValues();",60000);
}


// wrap for interval
function refreshAqiValues() {
    var req = new XMLHttpRequest();
    req.responseType = 'json';
    req.open('GET', 'https://data.lpb-air.com', true);
    req.setRequestHeader('cache-control', 'no-cache');
    req.onload  = function() {
        var responseAqi = req.response;
        var timestamp = responseAqi['timestamp'];
        var aqiValue = responseAqi['aqi_value'];
        var aqiCategory = responseAqi['aqi_category'];
        setAqiValues(timestamp,aqiValue,aqiCategory);
        setAqiColors(aqiCategory);
        setWeatherDetails(responseAqi);
    };
    req.send();
}

function setAqiValues(timestamp,aqiValue,aqiCategory) {

    document.getElementById('aqiValue').innerHTML = aqiValue;
    document.getElementById('aqiCategory').innerHTML = aqiCategory;
    document.getElementById('timestamp').innerHTML = timestamp;

}

function setAqiColors(aqiCategory) {
    // parse config
    var colMain = colorConfig[aqiCategory][0];
    var colSecond = colorConfig[aqiCategory][1];
    var colFilter = colorConfig[aqiCategory][2];
    // apply topbox col
    document.getElementById('colorbox').style.backgroundColor = colMain;
    // apply border col
    var colBorder = document.getElementsByClassName('col_border');
    for (var i = 0; i < colBorder.length; i++) {
        colBorder[i].style.borderColor = colMain;
    };
    // apply light background change
    var lightBg = document.getElementsByClassName('light_background');
    for (var i = 0; i < lightBg.length; i++) {
        lightBg[i].style.backgroundColor = colSecond;
    };
    // apply color filter
    var colFilterElements = document.getElementsByClassName('col_filter');
    for (var i = 0; i < colFilterElements.length; i++) {
        colFilterElements[i].style.filter = colFilter;
    };
    // apply font color
    var colFontElements = document.getElementsByClassName('col_font');
    for (var i = 0; i < colFontElements.length; i++) {
        colFontElements[i].style.color = colMain;
    };
}

function setWeatherDetails(responseAqi) {
    // parse response
    var weatherIcon = responseAqi['weather_icon'];
    var weatherName = responseAqi['weather_name'];
    var temperature = Math.round(responseAqi['temperature'] * 10) / 10
    var windSpeed = responseAqi['wind_speed'];
    var humidity = Math.round(responseAqi['humidity']);
    var pressure = Math.round(responseAqi['pressure']);
    // weather icon
    weatherIconSrc = '/img/icon/' + weatherIcon + '.png';
    document.getElementById('weather_icon').src = weatherIconSrc;
    // weather name
    document.getElementById('weather_name').innerHTML = weatherName;
    // temperature
    document.getElementById('temperature').innerHTML = temperature;
    // wind speed
    document.getElementById('wind_speed').innerHTML = windSpeed;
    // humidity
    document.getElementById('humidity').innerHTML = humidity;
    // pressure
    document.getElementById('pressure').innerHTML = pressure;
}