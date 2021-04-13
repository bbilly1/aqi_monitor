""" handles monthly tasks """

import calendar
import json
import numpy as np
import pandas as pd

from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from os import path

from app.db_connect import db_connect, db_close


def get_epoch():
    """ returns epoch for last month and last month last year """
    # run within first 7 days of month
    now = datetime.now()
    # last month
    last_day = now.replace(day=1) - timedelta(days=1)
    month_start = last_day.replace(day=1,hour=0,minute=0,second=0)
    month_end = last_day.replace(hour=23,minute=59,second=59)
    # last year
    last_year = last_day.year - 1
    month_start_year = month_start.replace(year=last_year)
    m_start_year_next = month_start_year + timedelta(days=31)
    m_start_year_first = m_start_year_next.replace(day=1)
    month_end_year = (m_start_year_first - timedelta(days=1)).replace(hour=23,minute=59,second=59)
    # build tpl and return
    last_month_tpl = (month_start.strftime('%s'), month_end.strftime('%s'))
    last_year_tpl = (month_start_year.strftime('%s'), month_end_year.strftime('%s'))
    return last_month_tpl, last_year_tpl


def get_rows(last_month_tpl, last_year_tpl, config):
    """ get rows from postgres """
    conn, cur = db_connect(config)
    cur.execute(
        f'SELECT epoch_time, aqi_value FROM aqi \
        WHERE epoch_time > {last_month_tpl[0]} \
        AND epoch_time < {last_month_tpl[1]} \
        ORDER BY epoch_time DESC;'
    )
    rows_month = cur.fetchall()
    cur.execute(
        f'SELECT epoch_time, aqi_value FROM aqi \
        WHERE epoch_time > {last_year_tpl[0]} \
        AND epoch_time < {last_year_tpl[1]} \
        ORDER BY epoch_time DESC;'
    )
    rows_year = cur.fetchall()
    db_close(conn, cur)
    return rows_month, rows_year


def get_axis(rows_month, rows_year):
    """ takes rows and returns axis """
    # initial df
    x_timeline = [datetime.fromtimestamp(i[0]) for i in rows_month]
    y_aqi_values = [int(i[1]) for i in rows_month]
    data = {'timestamp': x_timeline, 'now_aqi': y_aqi_values}
    df = pd.DataFrame(data)
    indexed = df.set_index('timestamp')
    indexed.sort_values(by=['timestamp'], inplace=True)
    mean = indexed.resample('8h').mean().round()
    # reset timestamp to day
    mean.reset_index(level=0, inplace=True)
    mean['timestamp'] = mean['timestamp'].dt.strftime('%d %H:%M')
    mean.set_index('timestamp', inplace=True)
    # second df with last year data
    x_timeline = [datetime.fromtimestamp(i[0]) for i in rows_year]
    y_aqi_values = [int(i[1]) for i in rows_year]
    data = {'timestamp': x_timeline, 'year_aqi': y_aqi_values}
    df = pd.DataFrame(data)
    indexed = df.set_index('timestamp')
    indexed.sort_values(by=['timestamp'], inplace=True)
    year_mean = indexed.resample('8h').mean().round()
    # reset timestamp to day
    year_mean.reset_index(level=0, inplace=True)
    year_mean['timestamp'] = year_mean['timestamp'].dt.strftime('%d %H:%M')
    year_mean.set_index('timestamp', inplace=True)
    # merge the two
    mean['year_aqi'] = year_mean['year_aqi']
    mean.reset_index(level=0, inplace=True)
    mean.sort_values(by='timestamp', ascending=True, inplace=True)
    # return axis
    x = mean['timestamp']
    y_1 = mean['now_aqi']
    y_2 = mean['year_aqi']
    return x, y_1, y_2, mean


def write_monthly_plot(x, y_1, y_2, timestamp):
    """ plot last-7 only """
    # parse timestamp
    date_from = datetime.fromtimestamp(timestamp)
    date_title = date_from.strftime('%b %Y')
    month_short = date_from.strftime('%b')
    file_name = 'dyn/monthly/' + date_from.strftime('%Y-%m') + '.png'
    plt_title = f'AQI values for: {date_title}'
    # build ticks
    y_max = np.ceil(max(y_1.append(y_2))/50)*50 + 50
    x_range = np.arange(0, len(x), step=9)
    last_day = int(x.max().split()[0])
    x_numbers = np.arange(1, last_day + 1, step=3)
    x_dates = [f'{str(i).zfill(2)} {month_short}' for i in x_numbers]
    x_ticks = x_range, x_dates
    # plot
    plt.style.use('seaborn')
    plt.plot(x, y_1, color='#313131', label='this year')
    plt.plot(x, y_2, color='#666666', linestyle='dashed', label='last year')
    plt.fill_between(x, y_1, y2=0, where=(y_1 > 0), color='#85a762', interpolate=True)              # good
    plt.fill_between(x, y_1, y2=50, where=(y_1 > 50), color='#d4b93c', interpolate=True)            # moderate
    plt.fill_between(x, y_1, y2=100, where=(y_1 > 100), color='#e96843', interpolate=True)          # ufsg
    plt.fill_between(x, y_1, y2=150, where=(y_1 > 150), color='#d03f3b', interpolate=True)          # unhealthy
    plt.fill_between(x, y_1, y2=200, where=(y_1 > 200), color='#be4173', interpolate=True)          # vunhealthy
    plt.fill_between(x, y_1, y2=300, where=(y_1 > 300), color='#714261', interpolate=True)          # hazardous
    plt.fill_between(x, y_1, y2=0, where=(y_1 > 0), color='#ffffff', alpha=0.1, interpolate=True)   # soft
    plt.xticks(x_ticks[0], x_ticks[1])
    plt.yticks(np.arange(0, y_max, step=50))
    plt.title(plt_title, fontsize=20)
    plt.legend()
    plt.tight_layout()
    plt.savefig(file_name, dpi = 300)
    plt.figure()


def get_change(curr, year):
    """ helper function to get change on thresh """
    diff_avg = (curr - year) / curr
    if diff_avg <= -0.15:
        avg_change = 'down'
    elif diff_avg >= 0.15:
        avg_change = 'up'
    else:
        avg_change = 'same'
    return avg_change


def get_aqi(val):
    """ helper function to get aqi category """
    if val <= 50:
        category = 'Good'
    elif val > 50 and val <= 100:
        category = 'Moderate'
    elif val > 100 and val <= 150:
        category = 'Unhealthy for Sensitive Groups'
    elif val > 150 and val <= 200:
        category = 'Unhealthy'
    elif val > 200 and val <= 300:
        category = 'Very Unhealthy'
    else:
        category = 'Hazardous'
    return category


def write_monthly_json(mean, timestamp):
    """ write json file with monthly details """
    date_from = datetime.fromtimestamp(timestamp)
    file_name = 'dyn/monthly/' + date_from.strftime('%Y-%m') + '.json'
    # current
    curr_min = int(mean['now_aqi'].min())
    curr_max = int(mean['now_aqi'].max())
    curr_mean = int(mean['now_aqi'].mean())
    curr_cat = get_aqi(curr_mean)
    # last
    year_min = int(mean['year_aqi'].min())
    year_max = int(mean['year_aqi'].max())
    year_mean = int(mean['year_aqi'].mean())
    year_cat = get_aqi(year_mean)
    # change
    min_change = get_change(curr_min, year_min)
    max_change = get_change(curr_max, year_max)
    mean_change = get_change(curr_mean, year_mean)
    # build rows
    data_rows = []
    data_rows.append(['min: ', curr_min, year_min, min_change])
    data_rows.append(['max: ', curr_max, year_max, max_change])
    data_rows.append(['avg: ', curr_mean, year_mean, mean_change])
    data_rows.append(['avg aqi: ', curr_cat, year_cat, mean_change])
    # build dict
    monthly_dict = {}
    monthly_dict['data'] = data_rows
    # write to disk
    json_str = json.dumps(monthly_dict)
    with open(file_name, 'w') as f:
        f.write(json_str)


def monthly_found(timestamp):
    """ check if monthly graph already created """
    date_from = datetime.fromtimestamp(timestamp)
    file_name = 'dyn/monthly/' + date_from.strftime('%Y-%m') + '.png'
    found = path.isfile(file_name)
    return found


def create_monthly(config):
    """ check if last month plot exists, create if needed """
    last_month_tpl, last_year_tpl = get_epoch()
    timestamp = int(last_month_tpl[0])
    found = monthly_found(timestamp)
    if found:
        print('monthly already created, skipping...')
        return
    else:
        print('creating monthly graph and json file')
    # get rows
    rows_month, rows_year = get_rows(last_month_tpl, last_year_tpl, config)
    # get axis
    x, y_1, y_2, mean = get_axis(rows_month, rows_year)
    # write plot
    write_monthly_plot(x, y_1, y_2, timestamp)
    # write data json
    write_monthly_json(mean, timestamp)
