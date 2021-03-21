""" recreate json file to populate last year comparison table """

from datetime import datetime
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from app.db_connect import db_connect, db_close
from app.graph_pm import color_colums


def get_rows(config):
    """ get rows from last 10 days 
    and last 10 days one year ago """
    now = datetime.now()
    # last 10
    now_until = int(now.date().strftime('%s'))
    now_from = now_until - 10 * 24 * 60 * 60
    # last 10 one year ago
    year_until = now_until - 365 * 24 * 60 * 60
    year_from = now_until - 375 * 24 * 60 * 60
    # make the call
    conn, cur = db_connect(config)
    cur.execute(
        f'SELECT epoch_time, aqi_value FROM aqi \
        WHERE epoch_time > {now_from} \
        AND epoch_time < {now_until} \
        ORDER BY epoch_time DESC;'
    )
    now_rows = cur.fetchall()
    cur.execute(
        f'SELECT epoch_time, aqi_value FROM aqi \
        WHERE epoch_time > {year_from} \
        AND epoch_time < {year_until} \
        ORDER BY epoch_time DESC;'
    )
    year_rows = cur.fetchall()
    # close and return
    db_close(conn, cur)
    return now_rows, year_rows


def initial_df(now_rows, year_rows):
    """ build mean df with year data split into columns """
    # first df with current data
    x_timeline = [datetime.fromtimestamp(i[0]) for i in now_rows]
    y_aqi_values = [int(i[1]) for i in now_rows]
    data = {'timestamp': x_timeline, 'now_aqi': y_aqi_values}
    df = pd.DataFrame(data)
    indexed = df.set_index('timestamp')
    indexed.sort_values(by=['timestamp'], inplace=True)
    mean = indexed.resample('1d').mean().round()
    # second df with last year data
    x_timeline = [datetime.fromtimestamp(i[0]) for i in year_rows]
    y_aqi_values = [int(i[1]) for i in year_rows]
    data = {'timestamp': x_timeline, 'year_aqi': y_aqi_values}
    df = pd.DataFrame(data)
    indexed = df.set_index('timestamp')
    indexed.sort_values(by=['timestamp'], inplace=True)
    year_mean = indexed.resample('1d').mean().round()
    year_mean.reset_index(level=0, inplace=True)
    # merge the two
    mean.reset_index(level=0, inplace=True)
    mean['year_aqi'] = year_mean['year_aqi']
    mean.sort_values(by='timestamp', ascending=False, inplace=True)
    mean['timestamp'] = mean['timestamp'].dt.strftime('%d %b')
    # return result
    return mean


def write_df(mean):
    """ finalize df and compare values """
    # build temp column with diff
    mean['diff'] = (mean['now_aqi'] - mean['year_aqi']) / mean['now_aqi']
    mean['change'] = np.where(mean['diff'].abs() < 0.15, 'same', mean['diff'])
    mean['change'] = np.where(mean['diff'] <= -0.15, 'down', mean['change'])
    mean['change'] = np.where(mean['diff'] >= 0.15, 'up', mean['change'])
    del mean['diff']
    # build average row on top
    now_avg = mean['now_aqi'].mean()
    year_avg = mean['year_aqi'].mean()
    diff_avg = (now_avg - year_avg) / now_avg
    if diff_avg <= -0.15:
        avg_change = 'down'
    elif diff_avg >= 0.15:
        avg_change = 'up'
    else:
        avg_change = 'same'
    
    # build avg df
    avg_row = {'timestamp': 'avg 10 days', 'now_aqi': now_avg, 'year_aqi': year_avg, 'change': avg_change}
    new_row = pd.DataFrame(avg_row, index = [0]).round()
    mean = pd.concat([new_row, mean]).reset_index(drop = True)
    # convert to int
    mean['now_aqi'] = mean['now_aqi'].astype('int')
    mean['year_aqi'] = mean['year_aqi'].astype('int')
    # extract and write json from df
    mean_json = mean.to_json(orient='split')
    with open('dyn/year-table.json', 'w') as f:
        f.write(mean_json)


def write_graph(mean):
    """ recreate barchart with yearly comparison """
    # build axis
    mean.sort_index(inplace=True)
    x = mean['timestamp'].to_list()
    y_1 = mean['now_aqi'].to_list()
    y_2 = mean['year_aqi'].to_list()
    # build color lists
    col_y_1 = color_colums(y_1)
    col_y_2 = color_colums(y_2)
    # set ticks
    y_max = int(np.ceil(max(y_1 + y_2)/50) * 50 + 50)
    x_indexes = np.arange(len(x))
    # build plot
    width = 0.25
    plt_title = 'Daily avg AQI values compared to last year'
    plt.style.use('seaborn')
    # write bars
    plt.bar(x_indexes - (width / 2) - 0.02, y_1, color=col_y_1, width=width)
    plt.bar(x_indexes + (width / 2) + 0.02, y_2, color=col_y_2, width=width)
    plt.title(plt_title, fontsize=20)
    plt.yticks(np.arange(0, y_max, step=50))
    plt.xticks(ticks=x_indexes, labels=x)
    plt.tight_layout()
    plt.savefig('dyn/year-graph.png', dpi=300)
    plt.figure()


def rebuild_table(config):
    """ main function to recreate year comparison table """
    now_rows, year_rows = get_rows(config)
    mean = initial_df(now_rows, year_rows)
    write_df(mean)
    write_graph(mean)
    # done
    print('recreated year comparison graph and json file')
