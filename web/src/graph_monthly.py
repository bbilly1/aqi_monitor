""" handle all monthly tasks """

import json
from os import listdir

from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from matplotlib import pyplot as plt

from src.db import DatabaseConnect
from src.helper import plt_fill


class MonthStatus:
    """ check what needs to be done """

    ARCHIVE_PATH = 'static/dyn/monthly'
    FIRST_MONTH = (2021, 3)

    def __init__(self):
        self.missing = self.check_missing()
        self.missing_stamps = self.build_missing_timestamps()

    @staticmethod
    def get_epoch(now):
        """ create relevant timestamps for month passed as datetime """
        # last month
        m_start = datetime(now.year, now.month, day=1)
        if m_start.month < 12:
            m_end = datetime(
                m_start.year, m_start.month + 1, day=1
            ) - timedelta(seconds=1)
        elif m_start.month == 12:
            m_end = datetime(m_start.year + 1, 1, 1) - timedelta(seconds=1)
        m_stamp = (int(m_start.strftime('%s')), int(m_end.strftime('%s')))
        # last year
        y_start = m_start.replace(year=m_start.year - 1)
        if y_start.month < 12:
            y_end = datetime(
                y_start.year, y_start.month + 1, day=1
            ) - timedelta(seconds=1)
        elif y_start.month == 12:
            y_end = datetime(y_start.year + 1, 1, 1) - timedelta(seconds=1)
        y_stamp = (int(y_start.strftime('%s')), int(y_end.strftime('%s')))
        return (m_stamp, y_stamp)

    def check_missing(self):
        """ check if current months already exists """
        today = datetime.now()
        last_month = datetime(
            today.year, today.month, day=1
        ) - timedelta(seconds=1)
        m_stamp, _ = self.get_epoch(last_month)
        all_files = [i for i in listdir(self.ARCHIVE_PATH) if '.png' in i]

        exported = []
        for file in all_files:
            year, month = file.split('.')[0].split('-')
            exported.append((int(year), int(month)))

        current_m = datetime.fromtimestamp(m_stamp[0])
        years = range(self.FIRST_MONTH[0], current_m.year + 1)

        missing = []
        for year in years:
            if year == self.FIRST_MONTH[0]:
                months = range(self.FIRST_MONTH[1], current_m.month + 1)
            else:
                months = range(1, current_m.month + 1)

            missing = [(year, i) for i in months if (year, i) not in exported]

        return missing

    def build_missing_timestamps(self):
        """ build timestamps for missing months """
        missing_stamps = []

        for missing_month in self.missing:
            year, month = missing_month
            time_obj = datetime(year, month, 2)
            missing_stamp = self.get_epoch(time_obj)
            missing_stamps.append(missing_stamp)

        return missing_stamps


class MonthGenerator():
    """ create the monthly graph and json table """

    def __init__(self, timestamps):
        self.m_stamp, self.y_stamp = timestamps
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
        # skip if empty
        if len(indexed) == 0:
            y_mean = indexed
        else:
            y_mean = indexed.resample('8h').mean().round()
        # reset timestamp to day
        y_mean.reset_index(level=0, inplace=True)
        if len(indexed):
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
        y_1 = self.axis['y_1'].replace(0, 1)
        y_2 = self.axis['y_2'].replace(0, 1)
        # parse timestamp
        date_month = datetime.fromtimestamp(self.m_rows[-1][0]).date()
        date_title = date_month.strftime('%b %Y')
        date_file = date_month.strftime('%Y-%m')
        month_short = date_month.strftime('%b')
        file_name = 'static/dyn/monthly/' + date_file + '.png'
        print(f'exporting graph for {date_title}')
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
        # skip if nan
        if y_val == 'nan':
            return y_val

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
        try:
            y_min = int(self.axis['y_2'].min())
            y_max = int(self.axis['y_2'].max())
            y_avg = int(self.axis['y_2'].mean())
            y_cat = self.get_aqi(y_avg)
        except ValueError:
            y_min = 'nan'
            y_max = 'nan'
            y_avg = 'nan'
            y_cat = 'nan'
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
    if not month_status.missing:
        print('all monthly already created, skipping...')
        return

    # create
    print('creating monthly graph and json file')
    for month in month_status.missing_stamps:
        month_generator = MonthGenerator(month)
        month_generator.write_plt()
        month_generator.write_table()
