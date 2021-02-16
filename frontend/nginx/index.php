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
                <img src="/img/cloud.png" alt="cloud" id="cloud">
                <div class="aqi_box">
                    <h1 id="aqiValue"></h1>
                    <h2 id="aqiCategory"></h2>
                </div>
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