""" creates the PM 2.5 and pm 10 graphs """

from datetime import datetime

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

from app.db_connect import db_connect, db_close


def color_colums(y):
    """ helper function to color bar columns """
    col = []
    for val in y:
        if val <= 50:
            # good
            col.append('#85a762')
        elif val > 50 and val <= 100:
            # moderate
            col.append('#d4b93c')
        elif val > 100 and val <= 150:
            # ufsg
            col.append('#e96843')
        elif val > 150 and val <= 200:
            # unhealthy
            col.append('#d03f3b')
        elif val > 200 and val <= 300:
            # vunhealthy
            col.append('#be4173')
        else:
            # hazardous
            col.append('#714261')
    return col


def get_pm_data(config):
    """ gets last 10 days worth of data"""
    now = datetime.now()
    day_until = int(now.date().strftime('%s'))
    day_from = day_until - 10 * 24 * 60 * 60
    conn, cur = db_connect(config)
    cur.execute(
        f'SELECT epoch_time, pm25, pm10 FROM aqi \
        WHERE epoch_time > {day_from} \
        AND epoch_time < {day_until} \
        ORDER BY epoch_time DESC;'
    )
    rows = cur.fetchall()
    db_close(conn, cur)
    return rows


def get_pm_axis(rows):
    """ build axis """
    # build dataframe
    x_timeline = [datetime.fromtimestamp(i[0]) for i in rows]
    y_pm25_values = [int(i[1]) for i in rows]
    y_pm10_values = [int(i[2]) for i in rows]
    data = {
        'timestamp': x_timeline, 
        'pm25': y_pm25_values, 
        'pm10': y_pm10_values
    }
    df = pd.DataFrame(data)
    indexed = df.set_index('timestamp')
    indexed.sort_values(by=['timestamp'], inplace=True, ascending=True)
    mean = indexed.resample('1d').mean()
    mean.reset_index(level=0, inplace=True)
    # axis
    mean['pm25'] = mean['pm25'].round()
    mean['pm10'] = mean['pm10'].round()
    x = mean['timestamp']
    y_1 = mean['pm25']
    y_2 = mean['pm10']
    return x, y_1, y_2


def build_pm_plot(x, y, y_max, thresh, title):
    """ write plots to file """
    file_name = title.replace('.', '')
    # make ticks
    x_range = np.arange(10).tolist()
    x_date_time = pd.to_datetime(x).dt.date.unique()
    x_dates = [i.strftime('%d %b') for i in x_date_time]
    # color
    col = []
    for val in y:
        if val < thresh:
            col.append('#6ecd65')
        else:
            col.append('#ff4d4d')
    # title
    plt_title = f'Daily avg PM {title} exposure'
    # plot
    plt.style.use('seaborn')
    plt.bar(x_dates, y, color=col, width=0.5)
    plt.axhline(y=thresh, color='#6ecd65', linestyle=':')
    plt.xticks(ticks=x_range, labels=x_dates)
    plt.yticks(np.arange(0, y_max, step=25))
    plt.title(plt_title, fontsize=20)
    plt.tight_layout()
    plt.savefig(f'dyn/pm{file_name}.png', dpi=300)
    plt.close('all')
    plt.figure()


def rebuild_pm_bar(config):
    """ main function to rebuild pm2.5 and pm10 values """
    # get data
    rows = get_pm_data(config)
    x, y_1, y_2 = get_pm_axis(rows)
    # max
    y_max = np.ceil(max(y_1.append(y_2))/25)*25 + 25
    # pm 2.5
    build_pm_plot(x, y_1, y_max, thresh=25, title='2.5')
    # pm 10
    build_pm_plot(x, y_2, y_max, thresh=50, title='10')
    # done
    print('recreated PM 2.5 and PM 10 graphs')


# hour bar chart
def get_hour_data(config):
    """ get last three days worth of data from postgres """
    # time
    now = datetime.now()
    day_until = int(now.date().strftime('%s'))
    day_from = day_until - 3 * 24 * 60 * 60
    # call db
    conn, cur = db_connect(config)
    cur.execute(
        f'SELECT epoch_time, aqi_value FROM aqi \
        WHERE epoch_time > {day_from} \
        AND epoch_time < {day_until} \
        ORDER BY epoch_time DESC;'
    )
    rows = cur.fetchall()
    db_close(conn, cur)
    return rows


def get_hour_axis(rows):
    """ build x and y from the rows """
    x_timeline = [datetime.fromtimestamp(i[0]) for i in rows]
    y_aqi_values = [int(i[1]) for i in rows]
    # build dataframe
    data = {'timestamp': x_timeline, 'aqi': y_aqi_values}
    df = pd.DataFrame(data)
    indexed = df.set_index('timestamp')
    indexed.sort_values(by=['timestamp'], inplace=True)
    mean = indexed.resample('1h').mean()
    # regroup by hour
    mean_hour = mean.groupby([mean.index.hour]).mean()
    mean_hour.reset_index(level=0, inplace=True)
    # set axis
    x = mean_hour['timestamp']
    y = mean_hour['aqi'].round()
    return x, y


def build_hour_plot(x, y):
    """ takes x and y and writes plot to file """
    plt_title = 'Last three days average AQI for each hour'
    # ticks
    x_range = np.arange(0, 24, step=3)
    x_hours = [str(i).zfill(2) + ":00" for i in x_range]
    y_max = np.ceil(max(y)/50) * 50 + 50
    # color columns
    col = color_colums(y)
    # create plot
    plt.style.use('seaborn')
    plt.bar(x, y, color=col, width=0.5)
    plt.yticks(np.arange(0, y_max, step=50))
    plt.xticks(ticks=x_range, labels=x_hours)
    plt.title(plt_title, fontsize=20)
    plt.tight_layout()
    plt.savefig('dyn/hours.png', dpi=300)
    plt.close('all')
    plt.figure()


def rebuild_hour_bar(config):
    """ main function to rebuild houly bar avg """
    rows = get_hour_data(config)
    x, y = get_hour_axis(rows)
    build_hour_plot(x, y)
