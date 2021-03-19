// main entry on load
const startInterval = async () => {
    await refreshAqiValues();
    setInterval("refreshAqiValues();",60000);
    setInterval("refreshImg();",300000);
    await new Promise(resolve => setTimeout(resolve, 1000));
    rmPreload();
}
window.addEventListener('load', startInterval);


var colorConfig = 
{
    // green
    'Good': [
        "#85a762", "#dbe4d1",
        "invert(66%) sepia(11%) saturate(1318%) hue-rotate(47deg) brightness(92%) contrast(86%)",
        "AQI 0 to 50",
        "Good: No health concerns, enjoy activities."
    ], 
    // yellow
    'Moderate': [
        "#d4b93c", "#f9f0c7",
        "invert(79%) sepia(5%) saturate(4660%) hue-rotate(9deg) brightness(89%) contrast(103%)",
        "AQI 51 - 100:",
        "Moderate: Active children and adults, and people with respiratory disease, such as asthma, should limit prolonged outdoor exertion."
    ], 
    // orange
    'Unhealthy for Sensitive Groups': [
        "#e96843", "#f8d0c8",
        "invert(61%) sepia(93%) saturate(3252%) hue-rotate(333deg) brightness(95%) contrast(91%)",
        "AQI 101 - 150:",
        "Unhealthy for Sensitive Groups: Active children and adults, and people with respiratory disease, such as asthma, should limit prolonged outdoor exertion."
    ],
    // red
    'Unhealthy': [
        "#d03f3b", "#f1c5c4",
        "invert(39%) sepia(16%) saturate(2264%) hue-rotate(314deg) brightness(97%) contrast(110%)",
        "AQI 151 - 200:",
        "Unhealthy: Everyone may begin to experience health effects: Active children and adults, and people with respiratory disease, such as asthma, should avoid prolonged outdoor exertion; everyone else, especially children, should limit prolonged outdoor exertion."
    ],
    // pink
    'Very Unhealthy': [
        "#be4173", "#e9c9d6",
        "invert(45%) sepia(32%) saturate(3238%) hue-rotate(308deg) brightness(77%) contrast(90%)",
        "AQI 201 - 300:",
        "Very Unhealthy: Active children and adults, and people with respiratory disease, such as asthma, should avoid all outdoor exertion; everyone else, especially children, should limit outdoor exertion."
    ],
    // violet
    'Hazardous': [
        "#714261", "#d7c6d0",
        "invert(31%) sepia(8%) saturate(2659%) hue-rotate(268deg) brightness(91%) contrast(88%)",
        "AQI 301 - 500:",
        "Hazardous: Everyone should avoid all outdoor exertion."
    ]
}


// remove preload cloud gif
function rmPreload() {
    const preload = document.querySelector('.preload');
    preload.classList.add('preload-finish');
    // scrollbar
    document.querySelector('body').style.overflow = 'unset'
    // sticky
    const topBar = document.querySelector('.colorbox');
    topBar.style.position = 'sticky';
    topBar.style.position = '-webkit-sticky';
}

// reload current.png from remote
function refreshImg() {
    var timestamp = new Date().getTime();
    var newLink = "/dyn/current.png?t=" + timestamp;
    var lastThreeImg = document.getElementById('last3-img');
    var lastThreeA = document.getElementById('last3-a');
    try {
        lastThreeImg.src = newLink;
        lastThreeA.href = newLink;
    } catch(e) {
        // console.log('no link to change');
    }
}

// wrap for interval
function refreshAqiValues() {
    return new Promise((resolve, reject) => {
        var req = new XMLHttpRequest();
        req.responseType = 'json';
        req.open('GET', '/dyn/air.json', true);
        req.setRequestHeader('cache-control', 'no-cache');
        req.onload = function() {
            var responseAqi = req.response;
            var timestamp = responseAqi['timestamp'];
            var aqiValue = responseAqi['aqi_value'];
            var aqiCategory = responseAqi['aqi_category'];
            setAqiValues(timestamp,aqiValue,aqiCategory);
            setAqiColors(aqiCategory);
            try {
                setWeatherDetails(responseAqi);
            } catch(e) {
                // console.log('no weather box found');
            };
            try {
                setDesc(responseAqi);
            } catch(e) {
                // console.log('no desc box found');
            };
        };
        req.send();
        resolve(true);
    });
}

function setAqiValues(timestamp,aqiValue,aqiCategory) {

    var aqiValueField = document.getElementById('aqiValue');
    if (aqiValueField) {
        aqiValueField.innerHTML = aqiValue;
    };

    var aqiCategoryField = document.getElementById('aqiCategory');
    if (aqiCategoryField) {
        aqiCategoryField.innerHTML = aqiCategory;
    };

    var timestampField = document.getElementById('timestamp');
    if (timestampField) {
        timestampField.innerHTML = timestamp;
    };
}

function setAqiColors(aqiCategory) {
    // parse config
    var colMain = colorConfig[aqiCategory][0];
    var colSecond = colorConfig[aqiCategory][1];
    var colFilter = colorConfig[aqiCategory][2];
    // apply topbox col
    var colorboxList = document.getElementsByClassName('colorbox');
    for (var i = 0; i < colorboxList.length; i++) {
        colorboxList[i].style.backgroundColor = colMain;
    }
    // apply border col
    var colBorder = document.getElementsByClassName('col_border');
    if (colBorder) {
        for (var i = 0; i < colBorder.length; i++) {
            colBorder[i].style.borderColor = colMain;
        };
    }
    // apply light background change
    var lightBg = document.getElementsByClassName('light_background');
    if (lightBg) {
        for (var i = 0; i < lightBg.length; i++) {
            lightBg[i].style.backgroundColor = colSecond;
        };
    }
    // apply color filter
    var colFilterElements = document.getElementsByClassName('col_filter');
    if (colFilterElements) {
        for (var i = 0; i < colFilterElements.length; i++) {
            colFilterElements[i].style.filter = colFilter;
        };
    }
    // apply font color
    var colFontElements = document.getElementsByClassName('col_font');
    if (colFontElements) {
        for (var i = 0; i < colFontElements.length; i++) {
            colFontElements[i].style.color = colMain;
        };
    }
    // apply hover color
    var css = '.nav li:hover {background-color: ' + colMain + ';}';
    var style = document.createElement('style');
    style.appendChild(document.createTextNode(css));
    document.getElementsByTagName('head')[0].appendChild(style);
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

function setDesc(responseAqi) {
    // parse response
    var aqiCategory = responseAqi['aqi_category'];
    var aqiCatClean = aqiCategory.toLowerCase().replaceAll(' ', '');
    var iconSrc = '/img/icon/category-' + aqiCatClean + ".png";
    // parse config
    var aqiRange = colorConfig[aqiCategory][3];
    var aqiDesc = colorConfig[aqiCategory][4];
    // set values
    document.getElementById('categoryIcon').src = iconSrc;
    document.getElementById('aqiName').innerHTML = aqiCategory;
    document.getElementById('aqiRange').innerHTML = aqiRange;
    document.getElementById('aqiDesc').innerHTML = aqiDesc;
    // remove active if any
    var active = document.querySelector(".active");
    if (active) {
        active.classList.remove("active");
    };
    // figure out which to activate
    var allCategories = Object.keys(colorConfig);
    var indexMatch = allCategories.indexOf(aqiCategory);
    var activeCat = document.getElementsByClassName('desc_item')[indexMatch];
    // activate
    activeCat.classList.add("active");
}
