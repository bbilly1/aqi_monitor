<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/css/style.css">
    <link rel="stylesheet" href="/css/lightbox.css">
    <title>AQI</title>
    <script src="/js/aqi.js"></script>
    <script src="/js/lightbox.js"></script>
    <meta property="og:title" content="Live Air Quality in Luang Prabang Laos PDR" />
    <meta property="og:url" content="https://www.lpb-air.com/" />
    <meta property="og:image" content="https://www.lpb-air.com/img/social_preview.jpg" />
    <meta property="og:type" content="website" />
    <meta property="og:description" content="Real-time and on site air quality measurment and changes over time." />
</head>
<body>
    <div class="preload">
        <img src="/img/cloud_colors.gif" alt="cloud_animation">
    </div>
    <div class="block_wrap light_background">
        <?php include($_SERVER['DOCUMENT_ROOT'] . '/incl/topnav.php'); ?>
        <div class="top_content content">
            <div class="cloud">
                <img src="/img/cloud.png" alt="cloud" class="col_filter">
                <div class="aqi_box">
                    <h1 id="aqiValue"></h1>
                    <p id="aqi-label">US AQI</p>
                    <h2 id="aqiCategory"></h2>
                </div>
            </div>
        </div>
    </div>
    <div class="block_wrap">
        <div class="weather_content content">
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
    <div class="block_wrap light_background">
        <div class="desc_content content">
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
    <div class="block_wrap">
        <div class="graph2 content">
            <div class="graph_item">
                <h3 id="last3">Last three hours</h3>
                <a href="/dyn/current.png" data-lightbox="graph" id="last3-a">
                    <img src="/dyn/current.png" alt="current" id="last3-img">
                </a>
            </div>
            <div class="graph_item">
                <h3 id=last7>Last 7 days</h3>
                <a href="/dyn/last-7.png" data-lightbox="graph">
                    <img src="/dyn/last-7.png" alt="last-7 days">
                </a>
            </div>
        </div>
    </div>
    <?php include($_SERVER['DOCUMENT_ROOT'] . '/incl/footer.html'); ?>
</body>
</html>