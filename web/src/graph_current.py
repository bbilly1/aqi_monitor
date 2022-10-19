""" handle current graph export """

import shutil
from datetime import datetime

import numpy as np
import pandas as pd

from matplotlib import pyplot as plt

from src.db import DatabaseConnect
from src.helper import get_config, plt_fill

FALLBACK_GRAPH = "static/img/fallback.png"


class CurrentPlot:
    """ recreate the last 3h plot """

    CONFIG = get_config()
    FILENAME = 'static/dyn/current.png'

    def __init__(self):
        self.now = datetime.now()
        self.rows = self.get_data()
        self.axis = None

    def get_data(self):
        """ export from postgres """
        now_epoch = int(self.now.strftime('%s'))
        last_3h = now_epoch - 3 * 60 * 60

        query = ('SELECT epoch_time, aqi_value FROM aqi '
                    f'WHERE epoch_time > {last_3h} ORDER BY epoch_time DESC;')

        db_handler = DatabaseConnect()
        rows = db_handler.db_execute(query)
        db_handler.db_close()

        return rows

    def build_title(self):
        """ build title from timestamps """

        time_from = datetime.fromtimestamp(self.rows[-1][0]).strftime('%H:%M')
        time_until = datetime.fromtimestamp(self.rows[0][0]).strftime('%H:%M')
        plt_title = f'AQI values last 3h: {time_from} - {time_until}'

        return plt_title

    def build_axis(self):
        """ build plot axis """
        rows = self.rows
        x_timeline = [datetime.fromtimestamp(i[0]) for i in rows]
        y_aqi_values = [int(i[1]) for i in rows]
        data = {'timestamp': x_timeline, 'aqi': y_aqi_values}
        df = pd.DataFrame(data)

        indexed = df.set_index('timestamp')
        indexed.sort_values(by=['timestamp'], inplace=True)
        mean = indexed.resample('3min').mean()
        mean.interpolate(
            method='linear', limit=1, inplace=True, limit_area='inside'
        )
        mean.reset_index(level=0, inplace=True)
        mean['timestamp'] = mean['timestamp'].dt.strftime('%H:%M')
        mean['aqi'] = mean['aqi'].round()
        plt_title = self.build_title()
        # xticks
        x_ticks = []
        for num, i in enumerate(mean['timestamp']):
            minute = int(i.split(':')[1])
            if minute % 15 == 0:
                x_ticks.append(num)

        axis = {
            'x': mean['timestamp'],
            'y': mean['aqi'],
            'x_ticks': x_ticks,
            'plt_title': plt_title
        }
        self.axis = axis

    def write_plt(self):
        """ save plot to file """
        x = self.axis['x']
        y = self.axis['y'].replace(0, 1)
        x_ticks = self.axis['x_ticks']
        # calc ticks
        y_max = np.ceil(y.max()/50)*50 + 50
        # setup plot
        plt.style.use('seaborn')
        plt.plot(x, y, color='#313131',)
        # fill colors
        plt_fill(plt, x, y)
        # handle passing ticks and lables separatly
        if len(x_ticks) == 2:
            plt.xticks(x_ticks[0], x_ticks[1])
        else:
            plt.xticks(x_ticks)
        plt.yticks(np.arange(0, y_max, step=50))
        plt.title(self.axis['plt_title'], fontsize=20)
        plt.tight_layout()
        plt.savefig(self.FILENAME, dpi=300)
        plt.figure()
        plt.close('all')


def main():
    """ main function to export current plot """
    print('current graph export')
    current = CurrentPlot()
    if current.rows:
        current.build_axis()
        current.write_plt()
    else:
        print('no rows found to export current graph')
        shutil.copy(FALLBACK_GRAPH, current.FILENAME)
