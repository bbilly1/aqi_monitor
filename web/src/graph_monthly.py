""" handle all monthly tasks """

import json
from os import path

from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from matplotlib import pyplot as plt

from src.db import DatabaseConnect
from src.helper import plt_fill


class MonthStatus:
    """ check what needs to be done """

    def __init__(self):
        self.m_stamp, self.y_stamp = (None, None)
        self.get_epoch()
        self.found = self.check_needed()

    def get_epoch(self):
        """ create relevant timestamps """
        # last month
        now = datetime.now()
        m_end = datetime(now.year, now.month, day=1) - timedelta(seconds=1)
        m_start = datetime(m_end.year, m_end.month, day=1)
        m_stamp = (int(m_start.strftime('%s')), int(m_end.strftime('%s')))
        # last year
        y_now = now.replace(year=now.year - 1)
        y_end = datetime(y_now.year, y_now.month, day=1) - timedelta(seconds=1)
        y_start = datetime(y_end.year, y_end.month, day=1)
        y_stamp = (int(y_start.strftime('%s')), int(y_end.strftime('%s')))
        # set
        self.m_stamp = m_stamp
        self.y_stamp = y_stamp

    def check_needed(self):
        """ check if current months already exists """
        file_name = datetime.fromtimestamp(self.m_stamp[0]).strftime('%Y-%m')
        file_path = path.join('static/dyn/monthly', file_name + '.png')
        found = path.isfile(file_path)
        return found


class MonthGenerator(MonthStatus):
    """ create the monthly graph and json table """

    def __init__(self):
        super().__init__()
        self.m_rows, self.y_rows = self.get_data()
        self.axis = self.build_axis()

    def get_data(self):
        """ export from postgres """
        m_query = ('SELECT epoch_time, aqi_value FROM aqi WHERE '
                   f'epoch_time > {self.m_stamp[0]} AND '
                   f'epoch_time < {self.m_stamp[1]} '
                   'ORDER BY epoch_time DESC;')
        y_query = ('SELECT epoch_time, aqi_value FROM aqi WHERE '
                   f'epoch_time > {self.y_stamp[0]} AND '
                   f'epoch_time < {self.y_stamp[1]} '
                   'ORDER BY epoch_time DESC;')
        # make the call
        db_handler = DatabaseConnect()
        m_rows = db_handler.db_execute(m_query)
        y_rows = db_handler.db_execute(y_query)
        db_handler.db_close()
        return m_rows, y_rows

    def build_axis(self):
        """ build axis from rows """
        # initial df
        x_timeline = [datetime.fromtimestamp(i[0]) for i in self.m_rows]
        y_aqi_values = [int(i[1]) for i in self.m_rows]
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
        x_timeline = [datetime.fromtimestamp(i[0]) for i in self.y_rows]
        y_aqi_values = [int(i[1]) for i in self.y_rows]
        data = {'timestamp': x_timeline, 'year_aqi': y_aqi_values}
        df = pd.DataFrame(data)
        indexed = df.set_index('timestamp')
        indexed.sort_values(by=['timestamp'], inplace=True)
        y_mean = indexed.resample('8h').mean().round()
        # reset timestamp to day
        y_mean.reset_index(level=0, inplace=True)
        y_mean['timestamp'] = y_mean['timestamp'].dt.strftime('%d %H:%M')
        y_mean.set_index('timestamp', inplace=True)
        # merge the two
        mean['year_aqi'] = y_mean['year_aqi']
        mean.reset_index(level=0, inplace=True)
        mean.sort_values(by='timestamp', ascending=True, inplace=True)
        # return axis
        axis = {
            'x': mean['timestamp'],
            'y_1': mean['now_aqi'],
            'y_2': mean['year_aqi']
        }
        return axis

    def write_plt(self):
        """ write monthly plot """
        x = self.axis['x']
        y_1 = self.axis['y_1']
        y_2 = self.axis['y_2']
        # parse timestamp
        date_month = datetime.fromtimestamp(self.m_rows[-1][0]).date()
        date_title = date_month.strftime('%b %Y')
        date_file = date_month.strftime('%Y-%m')
        month_short = date_month.strftime('%b')
        file_name = 'static/dyn/monthly/' + date_file + '.png'
        # build ticks
        y_max = np.ceil(max(y_1.append(y_2)) / 50) * 50 + 50
        x_range = np.arange(0, len(x), step=9)
        last_day = int(x.max().split()[0])
        x_numbers = np.arange(1, last_day + 1, step=3)
        x_dates = [f'{str(i).zfill(2)} {month_short}' for i in x_numbers]
        x_ticks = x_range, x_dates
        # plot
        plt.style.use('seaborn')
        plt.plot(x, y_1, color='#313131', label='this year')
        plt.plot(
            x, y_2, color='#666666', linestyle='dashed', label='last year'
        )
        # fill colors
        plt_fill(plt, x, y_1)
        plt.xticks(x_ticks[0], x_ticks[1])
        plt.yticks(np.arange(0, y_max, step=50))
        plt.title(f'AQI values for: {date_title}', fontsize=20)
        plt.legend()
        plt.tight_layout()
        plt.savefig(file_name, dpi=300)
        plt.figure()

    @staticmethod
    def get_aqi(val):
        """ helper function to get aqi category """
        breakpoints = [
            ('Good', 0, 50),
            ('Moderate', 50, 100),
            ('Unhealthy for Sensitive Groups', 100, 150),
            ('Unhealthy', 150, 200),
            ('Very Unhealthy', 200, 300),
            ('Hazardous', 300, 500),
        ]

        for break_point in breakpoints:
            category, min_val, max_val = break_point
            if min_val < val <= max_val:
                # found it
                break

        return category

    @staticmethod
    def get_change(m_val, y_val):
        """ helper function to get change on thresh """
        diff_avg = (m_val - y_val) / m_val
        if diff_avg <= -0.15:
            avg_change = 'down'
        elif diff_avg >= 0.15:
            avg_change = 'up'
        else:
            avg_change = 'same'
        return avg_change

    def write_table(self):
        """ write json file with monthly details """
        date_month = datetime.fromtimestamp(self.m_rows[-1][0]).date()
        date_file = date_month.strftime('%Y-%m')
        file_name = 'static/dyn/monthly/' + date_file + '.json'
        # current
        m_min = int(self.axis['y_1'].min())
        m_max = int(self.axis['y_1'].max())
        m_avg = int(self.axis['y_1'].mean())
        m_cat = self.get_aqi(m_avg)
        # last
        y_min = int(self.axis['y_2'].min())
        y_max = int(self.axis['y_2'].max())
        y_avg = int(self.axis['y_2'].mean())
        y_cat = self.get_aqi(y_avg)
        # build dict
        monthly_dict = {
            'data': [
                ['min: ', m_min, y_min, self.get_change(m_min, y_min)],
                ['max: ', m_max, y_max, self.get_change(m_max, y_max)],
                ['avg: ', m_avg, y_avg, self.get_change(m_avg, y_avg)],
                ['avg aqi: ', m_cat, y_cat, self.get_change(m_avg, y_avg)]
            ]
        }
        # write to disk
        with open(file_name, 'w') as f:
            f.write(json.dumps(monthly_dict))


def main():
    """ main to export monthly graph an table json """
    # check if needed
    month_status = MonthStatus()
    if month_status.found:
        print('monthly already created, skipping...')
        return

    # create
    print('creating monthly graph and json file')
    month_generator = MonthGenerator()
    month_generator.write_plt()
    month_generator.write_table()
