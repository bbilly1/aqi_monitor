""" main entry page to handle all the routes """

import os
from datetime import datetime

from flask import Flask, render_template, request, app
from flask import url_for  # pylint: disable=unused-import
from flask_httpauth import HTTPBasicAuth
from apscheduler.schedulers.background import BackgroundScheduler


from src.helper import Table, get_config
from src.db import get_current, insert_data
from src.graph_current import main as current_graph
from src.graph_nightly import main as nightly_graph
from src.graph_monthly import main as monthly_graph

import matplotlib
matplotlib.use('Agg')

# start up
app = Flask(__name__)

CONFIG = get_config()
auth = HTTPBasicAuth()
aqi_user = CONFIG['aqi_monitor']
USER_DATA = {
    aqi_user['authUsername']: aqi_user['authPassword']
}

# initial export
print('initial export')
current_graph()
nightly_graph()
monthly_graph()

# start scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    current_graph, trigger="cron", minute='*/5', name='current_graph'
)
scheduler.add_job(
    nightly_graph, trigger="cron", day='*', hour='1', minute='1', name='night'
)
scheduler.add_job(
    nightly_graph, trigger="cron", day='*', hour='1', minute='2', name='month'
)
scheduler.start()


@auth.verify_password
def verify(username, password):
    """ get password """
    if not (username and password):
        return False
    return USER_DATA.get(username) == password


@app.route("/")
def home():
    """ home page """
    return render_template('home.html')


@app.route("/about")
def about():
    """ about page """
    return render_template('about.html', title='About')


@app.route("/graphs")
def graphs():
    """ graphs page """
    table = Table('static/dyn/year-table.json').create_table()
    return render_template('graphs.html', title='Graphs', table=table)


@app.route("/monthly")
def monthly():
    """ monthly statistics page """
    months = [i for i in os.listdir('static/dyn/monthly') if '.json' in i]
    months.sort(reverse=True)

    month_dicts = []
    for month in months:
        month_clean = os.path.splitext(month)[0]
        month_graph = os.path.join('static/dyn/monthly', month_clean + '.png')
        month_name = datetime.strptime(month_clean, "%Y-%m").strftime('%B %Y')
        month_json = os.path.join('static/dyn/monthly', month)
        table = Table(month_json).create_table()
        month_dict = {
            'month_graph': month_graph,
            'month_name': month_name,
            'table': table
        }
        month_dicts.append(month_dict)

    return render_template('monthly.html', title='Monthly', months=month_dicts)


@app.route("/data/in", methods=['POST'])
@auth.login_required
def ingest():
    """ handle post request from monitor """
    post_data = request.json
    print(post_data)
    insert_data(post_data)
    return 'ingest'


@app.route("/data/out")
def data():
    """ return data from db """
    json_data = get_current()
    return json_data
