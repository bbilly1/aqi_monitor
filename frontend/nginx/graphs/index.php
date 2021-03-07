<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/css/style.css">
    <link rel="stylesheet" href="/css/lightbox.css">
    <script src="/js/aqi.js"></script>
    <script src="/js/lightbox.js"></script>
    <title>Graphs</title>
</head>
<body>
    <div class="block_wrap light_background">
        <?php include($_SERVER['DOCUMENT_ROOT'] . '/incl/topnav.php'); ?>
    </div>
    <div class="block_wrap">
        <div class="content">
            <h1>Graphs</h1>
        </div>
        <div class="content">
            <h2 id="last3">Last three days</h2>
        </div>
        <div class="graph3 content">
            <div class="graph_item">
                <p>Three days ago</p>
                <a href="/dyn/day-3.png" data-lightbox="graph">
                    <img src="/dyn/day-3.png" alt="day-3">
                </a>
            </div>
            <div class="graph_item">
                <p>Two days ago</p>
                <a href="/dyn/day-2.png" data-lightbox="graph">
                    <img src="/dyn/day-2.png" alt="day-2">
                </a>
            </div>
            <div class="graph_item">
                <p>Yesterday</p>
                <a href="/dyn/day-1.png" data-lightbox="graph">
                    <img src="/dyn/day-1.png" alt="day-1">
                </a>
            </div>
        </div>
        <div class="content divider">
            <hr class="col_border">
        </div>
        <div class="content">
            <h2 id="pm">Particle Matter sizes</h2>
            <p><b>There is no healthy level of pollution.</b> Particle matter (PM) are defined in two different sizes: PM 2.5 which represents particle sizes smaller than 2.5 &#xB5;m or less than 1/20th of the diameter of a human hair and PM 10 which represents particle sizer smaller than 10 &#xB5;m or 1/5th of the diameter of a human hair.</p>
            <p>The <a href="https://www.who.int/news-room/fact-sheets/detail/ambient-(outdoor)-air-quality-and-health" target="_blank">WHO</a> is providing more details on their website regarding particle matter and their health implications. On <a href="https://en.wikipedia.org/wiki/Particulates" target="blank">Wikipedia</a> there are some interesting links to studies for further reading.</p>
        </div>
        <div class="graph2 content">
            <div class="graph_item">
                <a href="/dyn/pm25.png" data-lightbox="pm-bar">
                    <img src="/dyn/pm25.png" alt="pm 2.5 bar chart">
                </a>
            </div>
            <div>
                <h3>PM 2.5</h3>
                <p>Particle matter sizes smaller than 2.5&#xB5;m are the most problematic as these particles will find their way through the lungs into the bloodstream.</p>
                <p>The WHO Air quality guideline values set a 25 &#xB5;g/m&sup3; 24-hour average as an upper level threshold. In the 10 days overview you can see:</p>
                <p>Green: Daily average exposure below 25 &#xB5;g/m&sup3;<br>
                Red: Daily average exposure above 25 &#xB5;g/m&sup3;</p>
            </div>
        </div>
        <div class="graph2 content">
            <div class="graph_item">
                <a href="/dyn/pm10.png" data-lightbox="pm-bar">
                    <img src="/dyn/pm10.png" alt="pm 10 bar chart">
                </a>
            </div>
            <div>
                <h3>PM 10</h3>
                <p>The threshold for the daily average PM 10 exposure is set to 50 &#xB5;g/m&sup3; by the WHO. Particles this size can penetrate and lodge deep inside the lungs but are too big to enter the blood stream. For this reason the threshold is higher.</p>
                <p>In the 10 days overview you can see:</p>
                <p>Green: Daily average exposure below 50 &#xB5;g/m&sup3;<br>
                Red: Daily average exposure above 50 &#xB5;g/m&sup3;</p>
            </div>
        </div>
        <div class="content divider">
            <hr class="col_border">
        </div>
    </div>
    <div class="block_wrap">
        <div class="tagline_content content">
            <h2>Some more graphs are coming soon here!</h2>
        </div>
    </div>
    <?php include($_SERVER['DOCUMENT_ROOT'] . '/incl/footer.html'); ?>
</body>
</html>