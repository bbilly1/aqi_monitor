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
        <!-- list start -->
        <?php 
        foreach(array_reverse(glob($_SERVER['DOCUMENT_ROOT'] . '/dyn/monthly/*.png')) as $month) {
            $file_name = basename($month,".png");
            $json_file = $_SERVER['DOCUMENT_ROOT'] . '/dyn/monthly/'.$file_name.'.json';
            $json = json_decode(file_get_contents($json_file), true);
            $rows = $json['data'];
            $date = new DateTime($file_name);
            $date_str = $date->format('F Y');
            echo '<div class="content"><h2>'.$date_str.'</h2></div>';
            echo '<div class="graph2 content">';
            echo '<div class="graph_item"><a href="/dyn/monthly/'.$file_name.'.png" data-lightbox="monthly">';
            echo '<img src="/dyn/monthly/'.$file_name.'.png" alt="'.$file_name.'"></a></div>';
            echo '<div class="year-table"><table>';
            echo '<thead><tr><th></th><th>this year</th><th>last year</th><th>change</th></tr></thead>';
            echo '<tbody class="aqi-table">';
            foreach($rows as $row) {
                echo '<tr>';
                foreach($row as $cell) {
                    echo '<td>' . $cell . '</td>';
                }
                echo '</tr>';
            }
            echo '</tbody>';
            echo '</table></div>';
            echo '</div>'; 
        }
        ?>
        <!-- list end -->
    </div>
</body>
</html>