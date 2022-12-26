""" collection of helper function and classes """

import json

from flask_table import create_table, Col


def get_config():
    """ read config file """
    config_path = 'config.json'

    with open(config_path, 'r') as config_file:
        data = config_file.read()

    config = json.loads(data)

    return config


def plt_fill(plt, x, y):
    """ fill colors between break points """
    x_list = list(x)
    y_list = list(y)
    plt.fill_between(
        x_list, y_list, y2=0, where=(y > 0), color='#85a762', interpolate=True
    )  # good
    plt.fill_between(
        x_list, y_list, y2=50, where=(y > 50), color='#d4b93c', interpolate=True
    )  # moderate
    plt.fill_between(
        x_list, y_list, y2=100, where=(y > 100), color='#e96843', interpolate=True
    )  # ufsg
    plt.fill_between(
        x_list, y_list, y2=150, where=(y > 150), color='#d03f3b', interpolate=True
    )  # unhealthy
    plt.fill_between(
        x_list, y_list, y2=200, where=(y > 200), color='#be4173', interpolate=True
    )  # vunhealthy
    plt.fill_between(
        x_list, y_list, y2=300, where=(y > 300), color='#714261', interpolate=True
    )  # hazardous
    plt.fill_between(
        x_list, y_list, y2=0, where=(y > 0), color='#ffffff', alpha=0.1, interpolate=True
    )  # soft


class Table:
    """ create html table from filename to pass to template """

    COLUMNS = [' ', 'this year', 'last year', 'change']

    def __init__(self, filename):
        self.filename = filename
        self.rows = self.get_rows()

    def get_rows(self):
        """ read filename to build rows dict """

        with open(self.filename, 'r') as json_file:
            json_raw = json_file.read()

        table_json = json.loads(json_raw)

        rows = []
        for i in table_json['data']:
            row = dict(zip(self.COLUMNS, i))
            rows.append(row)

        return rows

    def create_table(self):
        """ create the table with rows and columns """

        blank_table = create_table(options={'classes': ['comp-table']})

        for i in self.COLUMNS:
            blank_table.add_column(i, Col(i))

        table_obj = blank_table(self.rows)
        return table_obj
