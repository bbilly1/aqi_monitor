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
    x, y = build_plt(rows, sample_rate)
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


def build_plt(rows, sample_rate):
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
    mean['timestamp'] = mean['timestamp'].dt.strftime('%H:%M')
    mean['aqi'] = mean['aqi'].round()
    # set axis
    x = mean['timestamp']
    y = mean['aqi']
    # build title
    return x, y


def write_plt(x, y, plt_title, x_ticks, file_name):
    """ save plot to file """
    # calc ticks
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
    plt.xticks(x_ticks)
    plt.yticks(np.arange(0, y_max, step=50))
    plt.title(plt_title)
    plt.tight_layout()
    plt.savefig(f'dyn/{file_name}.png', dpi = 300)
    plt.figure()
