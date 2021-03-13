<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/css/style.css">
    <title>About</title>
    <script src="/js/aqi.js"></script>
</head>
<body>
    <div class="preload">
        <img src="/img/cloud_colors.gif" alt="cloud_animation">
    </div>
    <div class="block_wrap light_background">
        <?php include($_SERVER['DOCUMENT_ROOT'] . '/incl/topnav.php'); ?>
    </div>
    <div class="block_wrap">
        <div class="content">
            <h2>About</h2>
            <p>This page and its contents are still under construction. More content is coming soon.</p>
            <p>The data for this page is collected from an air monitor located just outside of Luang Prabang, Laos. While we do our best, no guarantee is given for the accuracy of this data.</p>
            <p>The data is updated every 3 minutes. Contrary to international websites who measure the air pollution via satellite images and rely on estimates and averages, an on-site air monitor delivers real time values that paint a much more accurate picture of the local situation.</p>
            <p>Roughly, the Air Quality Index (AQI) is the internationally used air quality standard to measure the pollution of the air. It is divided into 6 levels, and according to these levels, certain health advices are given:</p>
        </div>
        <div class="aqidesc content">
            <div class="aqirow">
                <div class="leftcolumn">
                    <p>Aqi Values</p>
                </div>
                <div class="rightcolumn hide">
                    <p>Description</p>
                </div>
            </div>
            <div class="aqirow">
                <div class="leftcolumn category-class good">
                    <p>0 to 50:</p>
                </div>
                <div class="rightcolumn">
                    <p>Good: No health concerns, enjoy activities.</p>
                </div>
            </div>
            <div class="aqirow">
                <div class="leftcolumn category-class moderate">
                    <p>51 - 100:</p>
                </div>
                <div class="rightcolumn">
                    <p>Moderate: Active children and adults, and people with respiratory disease, such as asthma, should limit prolonged outdoor exertion.</p>
                </div>
            </div>
            <div class="aqirow">
                <div class="leftcolumn category-class ufsg">
                    <p>101 - 150:</p>
                </div>
                <div class="rightcolumn">
                    <p>Unhealthy for Sensitive Groups: Active children and adults, and people with respiratory disease, such as asthma, should limit prolonged outdoor exertion.</p>
                </div>
            </div>
            <div class="aqirow">
                <div class="leftcolumn category-class unhealthy">
                    <p>151 - 200:</p>
                </div>
                <div class="rightcolumn">
                    <p>Unhealthy: Everyone may begin to experience health effects: Active children and adults, and people with respiratory disease, such as asthma, should avoid prolonged outdoor exertion; everyone else, especially children, should limit prolonged outdoor exertion</p>
                </div>
            </div>
            <div class="aqirow">
                <div class="leftcolumn category-class vunhealthy">
                    <p>201 - 300:</p>
                </div>
                <div class="rightcolumn">
                    <p>Very Unhealthy: Active children and adults, and people with respiratory disease, such as asthma, should avoid all outdoor exertion; everyone else, especially children, should limit outdoor exertion.</p>
                </div>
            </div>
            <div class="aqirow">
                <div class="leftcolumn category-class hazardous">
                    <p>301 - 500:</p>
                </div>
                <div class="rightcolumn">
                    <p>Hazardous: Everyone should avoid all outdoor exertion.</p>
                </div>
            </div>
        </div>
        <div class="credits content">
            <h2>Credits</h2>
            <p>Partial Weather data, namely weather icon, weather description and windspeed are provided from <a href="https://openweathermap.org/ " target="_blank">openweather.org</a> API distributed under the <a href="https://openweathermap.org/full-price" target="_blank">Creative Commons Attribution-ShareAlike 4.0 Generic License</a>.</p>
            <p><a target="_blank" href="https://github.com/lokesh/lightbox2">Lightbox</a> made by Lokesh Dhakar, released under the <a target="_blank" href="https://raw.githubusercontent.com/lokesh/lightbox2/master/LICENSE">MIT license</a>.</p>
        </div>
    </div>
    <?php include($_SERVER['DOCUMENT_ROOT'] . '/incl/footer.html'); ?>
</body>
</html>