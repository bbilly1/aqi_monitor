""" makes the nice plots """

from datetime import datetime, timedelta

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import psycopg2

from app.db_connect import db_connect, db_close


def create_current(config):
    """ recreate current graph """
    # last three hours
    now = datetime.now()
    now_human = now.strftime('%c')
    now_epoch = int(now.strftime('%s'))
    last_3h = now_epoch - 3 * 60 * 60
    last_3h_limit = int(60 * 3)
    # connect
    conn, cur = db_connect(config)
    # get data
    cur.execute(
        f'SELECT epoch_time, aqi_value FROM aqi \
        WHERE epoch_time > {last_3h} ORDER BY epoch_time DESC \
        LIMIT {last_3h_limit};')
    rows = cur.fetchall()
    # close db
    db_close(conn, cur)
    # set title
    data_from = now.strftime("%Y-%m-%d")
    time_from = datetime.fromtimestamp(rows[-1][0]).strftime('%H:%M')
    time_until = datetime.fromtimestamp(rows[0][0]).strftime('%H:%M')
    plt_title = f'AQI values from: {data_from} {time_from} - {time_until}'
    # parse rows
    sample_rate = '3min'
    x, y = build_plt(rows, sample_rate, '%H:%M')
    # calc x_ticks
    x_ticks = []
    for num, i in enumerate(x):
        minute = int(i.split(':')[1])
        if minute % 15 == 0:
            x_ticks.append(num)
    # write plt
    file_name = 'current'
    write_plt(x, y, plt_title, x_ticks, file_name)
    message = f'recreated current graph: {now_human}'
    print(message)


def rebuild_3days(config):
    """ wrapper to recreate all three days of graphs """
    now = datetime.now()
    # get axis
    x_1, y_1, plt_title_1, x_ticks_1 = get_axis(1, now, config)
    x_2, y_2, plt_title_2, x_ticks_2 = get_axis(2, now, config)
    x_3, y_3, plt_title_3, x_ticks_3 = get_axis(3, now, config)
    # set max
    y_max = max(y_1.append(y_2).append(y_3)) + 50
    # write plot
    write_plt(x_1, y_1, plt_title_1, x_ticks_1, 'day-1', y_max)
    write_plt(x_2, y_2, plt_title_2, x_ticks_2, 'day-2', y_max)
    write_plt(x_3, y_3, plt_title_3, x_ticks_3, 'day-3', y_max)
    print('recreaded last three days plt')


def get_axis(day, now, config):
    """ recreate plot for single days """
    day_delta = now.date() - timedelta(days = day)
    day_from = int(day_delta.strftime('%s'))
    day_until = int(day_delta.strftime('%s')) + 60 * 60 * 24
    # make the SELECT
    conn, cur = db_connect(config)
    cur.execute(
        f'SELECT epoch_time, aqi_value FROM aqi \
        WHERE epoch_time > {day_from} \
        AND epoch_time < {day_until} \
        ORDER BY epoch_time DESC LIMIT 720;'
    )
    rows = cur.fetchall()
    db_close(conn, cur)
    # title
    time_stamp = day_delta.strftime('%Y-%m-%d')
    plt_title = f'AQI values from: {time_stamp}'
    # build plt
    x_ticks = np.arange(0, 97, step=8)
    sample_rate = '15min'
    x, y = build_plt(rows, sample_rate, '%H:%M')
    return x, y, plt_title, x_ticks


def rebuild_7days(config):
    """ recreate last-7 days from db """
    # setup
    file_name = 'last-7'
    sample_rate = '2h'
    now = datetime.now()
    day_until = int(now.date().strftime('%s'))
    day_from = day_until - 7 * 24 * 60 * 60
    # get data
    conn, cur = db_connect(config)
    cur.execute(
        f'SELECT epoch_time, aqi_value FROM aqi \
        WHERE epoch_time > {day_from} \
        AND epoch_time < {day_until} \
        ORDER BY epoch_time DESC LIMIT 30 * 24 * 7;'
    )
    rows = cur.fetchall()
    db_close(conn, cur)
    # title
    date_from = datetime.fromtimestamp(rows[-1][0]).strftime('%Y-%m-%d')
    date_until = datetime.fromtimestamp(rows[0][0]).strftime('%Y-%m-%d')
    plt_title = f'AQI values from: {date_from} until {date_until}'
    # build x and y of plot
    x, y = build_plt(rows, sample_rate, '%Y-%m-%d %H:%M')
    # make ticks
    x_range = np.arange(0, 84, step=12)
    x_date_time = pd.to_datetime(x).dt.date.unique()
    x_dates = np.asarray([i.strftime('%Y-%m-%d') for i in x_date_time])
    x_ticks = x_range, x_dates
    # write the plot
    write_plt(x, y, plt_title, x_ticks, file_name)
    print('recreaded last-7 days graph')


def build_plt(rows, sample_rate, time_format):
    """ parse rows returns axis"""
    # build x y
    x_timeline = [datetime.fromtimestamp(i[0]) for i in rows]
    y_aqi_values = [int(i[1]) for i in rows]
    # build dataframe
    data = {'timestamp': x_timeline, 'aqi': y_aqi_values}
    df = pd.DataFrame(data)
    # reindex as timeseries
    indexed = df.set_index('timestamp')
    indexed.sort_values(by=['timestamp'], inplace=True)
    mean = indexed.resample(sample_rate).mean()
    mean.reset_index(level=0, inplace=True)
    mean['timestamp'] = mean['timestamp'].dt.strftime(time_format)
    mean['aqi'] = mean['aqi'].round()
    # set axis
    x = mean['timestamp']
    y = mean['aqi']
    # build title
    return x, y


def write_plt(x, y, plt_title, x_ticks, file_name, y_max=''):
    """ save plot to file """
    # calc ticks
    if not y_max:
        y_max = np.ceil(y.max()/50)*50 + 50
    # setup plot
    plt.style.use('seaborn')
    plt.plot(x, y, color='#313131',)
    plt.fill_between(x, y, y2=0, where=(y > 0), color='#85a762', interpolate=True)              # good
    plt.fill_between(x, y, y2=50, where=(y > 50), color='#d4b93c', interpolate=True)            # moderate
    plt.fill_between(x, y, y2=100, where=(y > 100), color='#e96843', interpolate=True)          # ufsg
    plt.fill_between(x, y, y2=150, where=(y > 150), color='#d03f3b', interpolate=True)          # unhealthy
    plt.fill_between(x, y, y2=200, where=(y > 200), color='#be4173', interpolate=True)          # vunhealthy
    plt.fill_between(x, y, y2=300, where=(y > 300), color='#714261', interpolate=True)          # hazardous
    plt.fill_between(x, y, y2=0, where=(y > 0), color='#ffffff', alpha=0.1, interpolate=True)   # soft
    # handle passing ticks and lables separatly
    if len(x_ticks) == 2:
        plt.xticks(x_ticks[0], x_ticks[1])
    else:
        plt.xticks(x_ticks)
    plt.yticks(np.arange(0, y_max, step=50))
    plt.title(plt_title)
    plt.tight_layout()
    plt.savefig(f'dyn/{file_name}.png', dpi = 300)
    plt.figure()
