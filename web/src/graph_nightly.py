""" handle nightly graph export """

from datetime import datetime, timedelta
import json
import shutil

import numpy as np
import pandas as pd
import scipy  # pylint: disable=unused-import

from matplotlib import pyplot as plt

from src.db import DatabaseConnect
from src.helper import chart_fill, get_config, plt_fill

FALLBACK_GRAPH = "static/img/fallback.png"


class NightlyPlots:
    """ get nightly data """

    CONFIG = get_config()

    def __init__(self):
        self.now = datetime.now()
        print('get data from db')
        self.rows, self.y_rows = self.get_data()

    @staticmethod
    def color_colums(y):
        """ helper function to color bar columns """

        breakpoints = [
            ('#85a762', 0, 50),     # good
            ('#d4b93c', 50, 100),   # moderate
            ('#e96843', 100, 150),  # ufsg
            ('#d03f3b', 150, 200),  # unhealthy
            ('#be4173', 200, 300),  # vunhealthy
            ('#714261', 300, 500),  # hazardous
        ]

        colors = []
        for value in y:
            if isinstance(value, pd._libs.missing.NAType):
                colors.append('#ffffff')
            else:
                for break_point in breakpoints:
                    color, min_val, max_val = break_point
                    if min_val < value <= max_val:
                        # found it
                        colors.append(color)
                        break

        return colors

    def get_data(self):
        """ export from postgres """
        # current
        day_until = int(self.now.date().strftime('%s'))
        day_from = day_until - 10 * 24 * 60 * 60
        query = ('SELECT epoch_time, aqi_value, pm25, pm10 FROM aqi WHERE '
                 f'epoch_time > {day_from} AND epoch_time < {day_until} '
                 'ORDER BY epoch_time DESC;')
        # last year
        y_until = day_until - 365 * 24 * 60 * 60
        y_from = y_until - 10 * 24 * 60 * 60
        y_query = ('SELECT epoch_time, aqi_value FROM aqi WHERE '
                   f'epoch_time > {y_from} AND epoch_time < {y_until} '
                   'ORDER BY epoch_time DESC;')
        db_handler = DatabaseConnect()
        rows = db_handler.db_execute(query)
        y_rows = db_handler.db_execute(y_query)
        db_handler.db_close()

        return rows, y_rows

    def recreate_last_7(self):
        """ last seven days """
        day_until = int(self.now.date().strftime('%s'))
        day_from = day_until - 7 * 24 * 60 * 60
        rows = [i for i in self.rows if day_from < i[0] < day_until]
        date_from = datetime.fromtimestamp(day_from).strftime('%d %b')
        date_until = datetime.fromtimestamp(day_until).strftime('%d %b')
        plt_title = f'AQI values from: {date_from} until {date_until}'
        handler = LastSevenDays(rows, plt_title)
        if handler.rows:
            handler.create()
        else:
            handler.fallback()

    def recreate_last_3(self):
        """ last three days """
        handler = LastThreeDays(self.rows, self.now)
        if handler.rows:
            handler.create()
        else:
            handler.fallback()

    def recreate_pm_chart(self):
        """ recreating pm2.5 and pm10 charts """
        handler = PmGraphs(self.rows)
        if handler.rows:
            handler.create()
        else:
            handler.fallback()

    def recreate_hour_bar(self):
        """ recreate hourly average through day bar chart """
        day_until = int(self.now.date().strftime('%s'))
        day_from = day_until - 3 * 24 * 60 * 60
        rows = [i for i in self.rows if day_from < i[0] < day_until]
        handler = HourBar(rows)
        if handler.rows:
            handler.create()
        else:
            handler.fallback()

    def recreate_year_comparison(self):
        """ recreate year comparison chart and table for json """
        handler = YearComparison(self.rows, self.y_rows)
        if handler.rows:
            handler.create()
        else:
            handler.fallback()


class LastSevenDays:
    """ recreate last 7 days """

    FILENAME = 'static/dyn/last-7.png'

    def __init__(self, rows, plt_title):
        print('recreating last seven days')
        self.plt_title = plt_title
        self.rows = rows
        self.axis = False

    def fallback(self):
        """fallback for no data"""
        print("use fallback last seven days")
        shutil.copy(FALLBACK_GRAPH, self.FILENAME)

    def create(self):
        """create graphs"""
        self.build_axis()
        self.write_plt()

    def build_axis(self):
        """ calc x and y """
        x_timeline = [datetime.fromtimestamp(i[0]) for i in self.rows]
        y_aqi_values = [int(i[1]) for i in self.rows]
        data = {'timestamp': x_timeline, 'aqi': y_aqi_values}
        df = pd.DataFrame(data)
        indexed = df.set_index('timestamp')
        indexed.sort_values(by=['timestamp'], inplace=True)
        mean = indexed.resample('2h').mean()
        mean['avg'] = mean['aqi'].resample('1d').mean()
        mean['avg'] = mean.avg.shift(6)
        # set first and last
        mean.loc[mean.index[0], "avg"] = (mean['avg'].iloc[6] + mean['aqi'].iloc[0]) / 2
        mean.loc[mean.index[-1], "avg"] = (mean['avg'].iloc[-6] + mean['aqi'].iloc[-1]) / 2
        # smooth
        try:
            mean["avg"] = mean["avg"].interpolate(method="polynomial", order=3)
        except ValueError:
            mean["avg"] = mean["avg"].interpolate(method="polynomial", order=1)

        mean.reset_index(level=0, inplace=True)
        mean['timestamp'] = mean['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
        mean['aqi'] = mean['aqi'].round()
        mean['avg'] = mean['avg'].round()
        # make ticks
        x_range = np.arange(0, 84, step=12)
        x_date_time = pd.to_datetime(mean['timestamp']).dt.date.unique()
        x_dates = np.asarray([i.strftime('%d %b') for i in x_date_time])
        x_dates.resize(7, refcheck=False)
        x_ticks = x_range, x_dates
        # set axis
        self.axis = {
            "x": mean['timestamp'],
            "y_1": mean['aqi'],
            "y_2": mean['avg'],
            "x_ticks": x_ticks,
            "plt_title": self.plt_title
        }

    def write_plt(self):
        """ write last 7 days plot to disk """
        x = self.axis['x']
        y_1 = self.axis['y_1'].replace(0, 1)
        y_2 = self.axis['y_2'].replace(0, 1)
        x_ticks = self.axis['x_ticks']
        y_max = np.ceil(max(pd.concat([y_1, y_2]))/50)*50 + 50
        # plot
        plt.style.use('seaborn-v0_8')
        plt.plot(x, y_1, color='#313131', label='2hour avg')
        plt.plot(x, y_2, color='#cc0000', label='daily avg')
        # fill colors
        plt_fill(plt, x, y_1)
        # ticks and plot
        plt.xticks(x_ticks[0], x_ticks[1])
        plt.yticks(np.arange(0, y_max, step=50))
        plt.title(self.axis['plt_title'], fontsize=20)
        plt.legend()
        plt.tight_layout()
        plt.savefig(self.FILENAME, dpi=300)
        plt.figure()


class LastThreeDays:
    """ recreate last three days plot """

    def __init__(self, rows, now):
        print('recreating last three days')
        self.y_max = None
        self.now = now
        self.rows = rows

    def create(self):
        """create graphs"""
        self.rebuild_last_three()

    def fallback(self, r_from=1, r_to=4):
        """fallback for empty rows"""
        print("use fallback for last three days")
        for i in range(r_from, r_to):
            new_path = f"static/dyn/day-{i}.png"
            shutil.copy(FALLBACK_GRAPH, new_path)

    def rebuild_last_three(self):
        """ recreate all three graphs """
        # get axis
        all_axis = []
        for day in range(1, 4):
            axis = self.get_axis(day)
            if not axis:
                self.fallback(r_from=day, r_to=day + 1)
                continue

            all_axis.append(axis)
        # set y_max
        self.y_max = max([max(i['y']) for i in all_axis]) + 50
        # plt
        for idx, axis in enumerate(all_axis):
            day = idx + 1
            self.write_plt(axis, day)

    def get_axis(self, day):
        """ get axis for day passed in """
        day_delta = self.now.date() - timedelta(days=day)
        day_from = int(day_delta.strftime('%s'))
        day_until = int(day_delta.strftime('%s')) + 60 * 60 * 24
        day_rows = [i for i in self.rows if day_from < i[0] < day_until]
        if not day_rows:
            return False

        # title
        time_stamp = day_delta.strftime('%Y-%m-%d')
        # build
        x_timeline = [datetime.fromtimestamp(i[0]) for i in day_rows]
        y_aqi_values = [int(i[1]) for i in day_rows]
        data = {'timestamp': x_timeline, 'aqi': y_aqi_values}
        df = pd.DataFrame(data)
        indexed = df.set_index('timestamp')
        indexed.sort_values(by=['timestamp'], inplace=True)
        mean = indexed.resample('15min').mean()
        mean.interpolate(
            method='linear', limit=1, inplace=True, limit_area='inside'
        )
        mean.reset_index(level=0, inplace=True)
        mean['timestamp'] = mean['timestamp'].dt.strftime('%H:%M')
        mean['aqi'] = mean['aqi'].round()
        # set axis
        axis = {
            "x": mean['timestamp'],
            "y": mean['aqi'],
            "x_ticks": np.arange(0, 97, step=8),
            "plt_title": f'AQI values from: {time_stamp}'
        }
        return axis

    def write_plt(self, axis, day):
        """ write daily plot to disk """
        x = axis['x']
        y = axis['y'].replace(0, 1)
        x_ticks = np.arange(0, 97, step=8)
        plt.style.use('seaborn-v0_8')
        plt.plot(x, y, color='#313131',)
        # fill colors
        plt_fill(plt, x, y)
        # ticks and plot
        plt.xticks(x_ticks)
        plt.yticks(np.arange(0, self.y_max, step=50))
        plt.title(axis['plt_title'], fontsize=20)
        plt.tight_layout()
        plt.savefig(f'static/dyn/day-{day}.png', dpi=300)
        plt.figure()
        plt.close('all')


class PmGraphs:
    """ recreate avg pm10 and pm2.5 exposure graphs """

    def __init__(self, rows):
        print('recreating pm bar charts')
        self.rows = rows
        self.y_max = None
        self.axis = False

    def create(self):
        """create pm charts"""
        self.get_axis()
        self.write_plt(thresh=25, title='2.5')
        self.write_plt(thresh=50, title='10')

    def fallback(self):
        """use fallback for empty rows"""
        print("use fallback for pm charts")
        shutil.copy(FALLBACK_GRAPH, "static/dyn/pm10.png")
        shutil.copy(FALLBACK_GRAPH, "static/dyn/pm25.png")

    def get_axis(self):
        """ get pm2.5 and pm20 axis """
        x_timeline = [datetime.fromtimestamp(i[0]) for i in self.rows]
        y_pm25_values = [int(i[2]) for i in self.rows]
        y_pm10_values = [int(i[3]) for i in self.rows]
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
        self.axis = {
            'x': mean['timestamp'],
            'y_pm25': mean['pm25'].round(),
            'y_pm10': mean['pm10'].round()
        }
        # max
        self.y_max = np.ceil(
            max(pd.concat([self.axis['y_pm25'], self.axis['y_pm10']])) / 25
        ) * 25 + 25

    def write_plt(self, thresh, title):
        """ write plot to disk """
        file_name = title.replace('.', '')
        plt_title = f'Daily avg PM {title} exposure'
        x = self.axis['x']
        y = self.axis['y_pm' + file_name]
        # make ticks
        x_date_time = pd.to_datetime(x).dt.date.unique()
        x_range = np.arange(len(x_date_time)).tolist()
        x_dates = [i.strftime('%d %b') for i in x_date_time]
        # col
        col = []
        for val in y:
            if val < thresh:
                col.append('#6ecd65')
            else:
                col.append('#ff4d4d')
        # plot
        plt.style.use('seaborn-v0_8')
        plt.bar(x_dates, y, color=col, width=0.5)
        plt.axhline(y=thresh, color='#6ecd65', linestyle=':')
        plt.xticks(ticks=x_range, labels=x_dates)
        plt.yticks(np.arange(0, self.y_max, step=25))
        plt.title(plt_title, fontsize=20)
        plt.tight_layout()
        plt.savefig(f'static/dyn/pm{file_name}.png', dpi=300)
        plt.close('all')
        plt.figure()


class HourBar:
    """ recreate hour by our avg bar chart """

    FILENAME = "static/dyn/hours.png"

    def __init__(self, rows):
        print('recreating hour avg bar chart')
        self.rows = rows
        self.axis = False

    def create(self):
        """create hour bar chart"""
        self.get_axis()
        self.write_plt()

    def fallback(self):
        """fallback for empty rows"""
        shutil.copy(FALLBACK_GRAPH, self.FILENAME)

    def get_axis(self):
        """ get hourly bar chart axis """
        x_timeline = [datetime.fromtimestamp(i[0]) for i in self.rows]
        y_aqi_values = [int(i[1]) for i in self.rows]
        data = {
            'timestamp': x_timeline,
            'aqi': y_aqi_values
        }
        df = pd.DataFrame(data)
        indexed = df.set_index('timestamp')
        indexed.sort_values(by=['timestamp'], inplace=True)
        mean = indexed.resample('1h').mean()
        # regroup by hour
        mean_hour = mean.groupby([mean.index.hour]).mean()
        mean_hour.reset_index(level=0, inplace=True)
        self.axis = {
            'x': mean_hour['timestamp'],
            'y': mean_hour['aqi'].round()
        }

    def write_plt(self):
        """ write the hour bar chart to disk """
        plt_title = 'Last three days average AQI for each hour'
        x = self.axis['x']
        y = self.axis['y']
        # ticks
        x_range = np.arange(0, 24, step=3)
        x_hours = [str(i).zfill(2) + ":00" for i in x_range]
        y_max = np.ceil(max(y)/50) * 50 + 50
        # color columns
        col = NightlyPlots.color_colums(y)
        # create plot
        plt.style.use('seaborn-v0_8')
        plt.bar(x, y, color=col, width=0.5)
        plt.yticks(np.arange(0, y_max, step=50))
        plt.xticks(ticks=x_range, labels=x_hours)
        plt.title(plt_title, fontsize=20)
        plt.tight_layout()
        plt.savefig(self.FILENAME, dpi=300)
        plt.close('all')
        plt.figure()


class YearComparison:
    """ export year on year graph and table """

    PLT_FILENAME = "static/dyn/year-graph.png"
    TABLE_FILENAME = "static/dyn/year-table.json"

    def __init__(self, rows, y_rows):
        print('recreating year comparison')
        self.rows = rows
        self.y_rows = y_rows
        self.axis = False

    def create(self):
        """create year comparison graphs"""
        self.get_axis()
        self.write_table()
        self.write_plt()

    def fallback(self):
        """create fallback"""
        shutil.copy(FALLBACK_GRAPH, self.PLT_FILENAME)
        shutil.copy("static/year-table_fallback.json", self.TABLE_FILENAME)

    def get_axis(self):
        """ build axis """
        # first df with current data
        x_timeline = [datetime.fromtimestamp(i[0]) for i in self.rows]
        y_aqi_values = [int(i[1]) for i in self.rows]
        data = {'timestamp': x_timeline, 'now_aqi': y_aqi_values}
        df = pd.DataFrame(data)
        indexed = df.set_index('timestamp')
        indexed.sort_values(by=['timestamp'], inplace=True)
        mean = indexed.resample('1d').mean().round()
        mean.reset_index(level=0, inplace=True)
        # second df with last year data
        x_timeline = [datetime.fromtimestamp(i[0]) for i in self.y_rows]
        y_aqi_values = [int(i[1]) for i in self.y_rows]
        data = {'timestamp': x_timeline, 'year_aqi': y_aqi_values}
        df = pd.DataFrame(data)
        indexed = df.set_index('timestamp')
        indexed.sort_values(by=['timestamp'], inplace=True)
        # skip if empty
        if len(indexed) == 0:
            year_mean = indexed
        else:
            year_mean = indexed.resample('1d').mean().round()
        year_mean.reset_index(level=0, inplace=True)
        # merge the two
        mean['year_aqi'] = year_mean['year_aqi']
        mean.sort_values(by='timestamp', inplace=True)
        mean['timestamp'] = mean['timestamp'].dt.strftime('%d %b')
        # build diff
        mean['diff'] = (mean['now_aqi'] - mean['year_aqi']) / mean['now_aqi']
        mean['change'] = np.where(
            mean['diff'].abs() < 0.15, 'same', mean['diff']
        )
        mean['change'] = np.where(
            mean['diff'] <= -0.15, 'down', mean['change']
        )
        mean['change'] = np.where(mean['diff'] >= 0.15, 'up', mean['change'])
        # return axis
        self.axis = {
            'x': mean['timestamp'],
            'y_1': mean['now_aqi'],
            'y_2': mean['year_aqi'],
            'change': mean['change']
        }

    def write_table(self):
        """ write year comparison table json """
        # build average row on top
        avg = int(self.axis['y_1'].mean())
        # skip on empty
        try:
            y_avg = int(self.axis['y_2'].mean())
            diff_avg = (avg - y_avg) / avg
            if diff_avg <= -0.15:
                avg_change = 'down'
            elif diff_avg >= 0.15:
                avg_change = 'up'
            else:
                avg_change = 'same'
        except (TypeError, ValueError):
            y_avg = 'nan'
            avg_change = 'nan'
        avg_row = ('avg 10 days', avg, y_avg, avg_change)
        # zip it
        y_1 = self.axis['y_1'].astype("Int64").astype(str).replace("<NA>", "nan")
        y_2 = self.axis['y_2'].astype("Int64").astype(str).replace("<NA>", "nan")
        y_2_change = self.axis['change'].astype(str)
        zipped = zip(
            self.axis['x'], y_1,
            y_2, y_2_change
        )
        data_rows = list(zipped)
        data_rows.reverse()
        data_rows.insert(0, avg_row)
        json_dict = json.dumps({"data": data_rows})
        # write to file
        with open(self.TABLE_FILENAME, 'w') as f:
            f.write(json_dict)

    def write_plt(self):
        """write year comparison bar chart"""
        x = self.axis["x"]
        y_1 = self.axis["y_1"]
        y_2 = self.axis["y_2"].fillna(value=0)
        # set ticks
        y_max = int(np.ceil((max(pd.concat([y_1, y_2])) / 50)) * 50 + 50)
        y_ticks = np.arange(0, y_max, step=50)
        # build plot
        plt.title("Daily avg AQI values compared to last year", fontsize=15)
        chart_fill(plt, y_ticks)
        plt.style.use("seaborn-v0_8")
        plt.plot(x, y_1, color="#313131", label="this year")
        plt.plot(
            x, y_2, color="#666666", linestyle="dashed", label="last year"
        )
        plt.yticks(y_ticks)
        plt.legend()
        plt.legend(loc="lower center", bbox_to_anchor=(0.5, -0.02), ncol=2)
        plt.tight_layout()
        plt.savefig(self.PLT_FILENAME, dpi=300)
        plt.figure()


def main():
    """ collection of nightly exports """
    nightly = NightlyPlots()
    nightly.recreate_last_7()
    nightly.recreate_last_3()
    nightly.recreate_pm_chart()
    nightly.recreate_hour_bar()
    nightly.recreate_year_comparison()
