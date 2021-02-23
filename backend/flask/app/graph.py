""" makes the nice plots """

from datetime import datetime

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
        "SELECT epoch_time, aqi_value FROM aqi \
        WHERE epoch_time > " + str(last_3h) + " ORDER BY epoch_time DESC \
        LIMIT " + str(last_3h_limit) + ";")
    rows = cur.fetchall()
    # close db
    db_close(conn, cur)
    # parse rows
    x, y, plt_title = build_plt(rows, now)
    # calc x_ticks
    x_ticks = []
    for num, i in enumerate(x):
        minute = int(i.split(':')[1])
        if minute % 15 == 0:
            x_ticks.append(num)
    # write plt
    write_plt(x, y, plt_title, x_ticks)
    message = f'recreated current graph: {now_human}'
    print(message)


def build_plt(rows, now):
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
    mean = indexed.resample('3min').mean()
    mean.reset_index(level=0, inplace=True)
    mean['timestamp'] = mean['timestamp'].dt.strftime('%H:%M')
    mean['aqi'] = mean['aqi'].round()
    # set axis
    x = mean['timestamp']
    y = mean['aqi']
    # build title
    data_from = now.strftime("%Y-%m-%d")
    time_from = x_timeline[-1].strftime('%H:%M')
    time_until = x_timeline[0].strftime('%H:%M')
    plt_title = f'AQI values from: {data_from} {time_from} - {time_until}'
    return x, y, plt_title


def write_plt(x, y, plt_title, x_ticks):
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
    plt.savefig('dyn/current.png', dpi = 300)
    plt.figure()
