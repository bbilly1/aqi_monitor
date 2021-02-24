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
        <?php include($_SERVER['DOCUMENT_ROOT'] . '/incl/topnav.html'); ?>
    </div>
    <div class="block_wrap">
        <div class="content">
            <h1>Graphs</h1>
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
    </div>
    <div class="block_wrap">
        <div class="tagline_content content">
            <h2>Some more graphs are coming soon here!</h2>
        </div>
    </div>
</body>
</html>