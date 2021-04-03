<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/css/style.css">
    <link rel="stylesheet" href="/css/lightbox.css">
    <title>Monthly</title>
    <script src="/js/aqi.js"></script>
    <script src="/js/lightbox.js"></script>
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
            <h1>Month by month</h1>
            <p>Month compared to last year. Values are in 8h average.</p>
        </div>
        <div class="content">
            <h2>March 2021</h2>
        </div>
        <div class="graph2 content">
            <div class="graph_item">
                <a href="/dyn/monthly/2021-03.png" data-lightbox="monthly">
                    <img src="/dyn/monthly/2021-03.png" alt="2021-03">
                </a>
            </div>
            <div class="year-table monthly-table" data='2021-03'>
                <table>
                    <thead>
                        <tr>
                            <th></th>
                            <th>this year</th>
                            <th>last year</th>
                            <th>change</th>
                        </tr>
                    </thead>
                    <tbody id='2021-03'>
                        
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>