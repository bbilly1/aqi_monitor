<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="css/style.css">
    <script src="/js/aqi.js"></script>
    <title>AQI</title>
</head>
<body>
    <div class="colorbox" id="colorbox"></div>
    <div class="top_wrap light_background">
        <div class="top_content">
            <div class="title">
                <h1>Live Air Quality</h1>
                <h2>in Luang Prabang Laos PDR</h2>
                <p>Last updated: <span id="timestamp"></span></p>
            </div>
            <div class="cloud">
                <img src="/img/cloud.png" alt="cloud" class="col_filter">
                <div class="aqi_box">
                    <h1 id="aqiValue"></h1>
                    <h2 id="aqiCategory"></h2>
                </div>
            </div>
        </div>
    </div>
    <div class="weather_wrap">
        <div class="weather_content">
            <div class="weather_box col_border">
                <div class="weather_icon">
                    <img src="/img/icon/000.png" alt="weather_icon" class="col_filter" id="weather_icon">
                </div>
                <div class="weather_text">
                    <h3 class="col_font"><span id="temperature"></span><span> °C</span></h3>
                    <p id="weather_name"></p>
                </div>
            </div>
            <div class="weather_box col_border">
                <div class="weather_icon">
                    <img src="/img/icon/wind.png" alt="wind_icon" class="col_filter">
                </div>
                <div class="weather_text">
                    <h3 class="col_font">Wind</h3>
                    <p><span id="wind_speed"></span><span> km/h</span></p>
                </div>
            </div>
            <div class="weather_box col_border">
                <div class="weather_icon">
                    <img src="/img/icon/humidity.png" alt="humidity_icon" class="col_filter">
                </div>
                <div class="weather_text">
                    <h3 class="col_font">Humidity</h3>
                    <p><span id="humidity"></span><span> %</span></p>
                </div>
            </div>
            <div class="weather_box col_border">
                <div class="weather_icon">
                    <img src="/img/icon/pressure.png" alt="pressure_icon" class="col_filter">
                </div>
                <div class="weather_text">
                    <h3 class="col_font">Pressure</h3>
                    <p><span id="pressure"></span><span> mbar</span></p>
                </div>
            </div>
        </div>
    </div>
    <div class="desc_wrap light_background">
        <div class="desc_content">
            <div class="desc_box">
                <div class="desc_item_wrap">
                    <div class="desc_item good">
                        <p>GOOD</p>
                    </div>
                    <div class="desc_item moderate">
                        <p>MODERATE</p>
                    </div>
                    <div class="desc_item ufsg">
                        <p>UNHEALTHY FOR SENSITIVE GROUPS</p>
                    </div>
                    <div class="desc_item unhealthy">
                        <p>UNHEALTHY</p>
                    </div>
                    <div class="desc_item vunhealthy">
                        <p>VERY UNHEALTHY</p>
                    </div>
                    <div class="desc_item hazardous">
                        <p>HAZARDOUS</p>
                    </div>
                </div>
            </div>
            <div class="desc_box">
                <div class="category_icon">
                    <img src="/img/icon/category-plain.png" alt="category_icon" id="categoryIcon">
                </div>
            </div>
            <div class="desc_box">
                <h2 class="col_font" id="aqiName"></h2>
                <h3 id="aqiRange"></h3>
                <p id="aqiDesc">Good: No health concerns, enjoy activities.</p>
            </div>
        </div>
    </div>
    <div class="tagline_wrap">
        <div class="tagline_content">
            <h1>More is coming soon here!</h1>
        </div>
    </div>
</body>
</html>