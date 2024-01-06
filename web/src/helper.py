""" collection of helper function and classes """

import json

# from flask_table import create_table, Col


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


def chart_fill(plt, y_ticks):
    """fill line chart background"""
    key_map = {
        0: {
            "low": 0,
            "high": 50,
            "color": "#85a762",
            "name": "good",
        },
        50: {
            "low": 50,
            "high": 100,
            "color": "#d4b93c",
            "name": "moderate",
        },
        100: {
            "low": 100,
            "high": 150,
            "color": "#e96843",
            "name": "ufsg",
        },
        150: {
            "low": 150,
            "high": 200,
            "color": "#d03f3b",
            "name": "unhealthy",
        },
        200: {
            "low": 200,
            "high": 300,
            "color": "#be4173",
            "name": "vunhealthy",
        },
        250: {
            "low": 200,
            "high": 300,
            "color": "#be4173",
            "name": "vunhealthy",
        },
        300: {
            "low": 300,
            "high": y_ticks[-1],
            "color": "#714261",
            "name": "hazardous",
        }
    }

    for tick in y_ticks[0:-1]:
        if tick > 300:
            match = key_map[300]
        else:
            match = key_map[tick]

        plt.axhspan(
            match["low"], match["high"], facecolor=match["color"], zorder=0
        )


def get_table(path):
    """read json file from path"""
    with open(path, "r") as f:
        table_data = json.loads(f.read()).get("data")

    return table_data
