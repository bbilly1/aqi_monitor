"""entry point to collect data from sensors"""

import json
import sys

from os import path

import requests

from sensor_sds011 import SDS
from sensor_bme280 import BmeSensor


class PiSensor:
    """collect and send data"""

    SENSOR_ID = 1

    def __init__(self):
        self.data = False

    def get_data(self):
        """get all data from sensors"""
        self.data = {}
        self.get_sds011()
        self.get_bme()
        self.add_static()

    def get_sds011(self):
        """get data dict from sds011"""
        sds_data = SDS().collect()
        self.data.update(sds_data)

    def get_bme(self):
        """get data dict from bme"""
        bme_data = BmeSensor().collect()
        self.data.update(bme_data)

    def add_static(self):
        """add static values to data"""
        self.data.update(
            {
                "sensor_id": self.SENSOR_ID,
                "uptime": self.get_uptime(),
            }
        )

    @staticmethod
    def get_uptime():
        """read uptime"""
        with open("/proc/uptime", "r", encoding="utf-8") as f:
            uptime_seconds = float(f.readline().split()[0])

        return uptime_seconds

    def send_data(self):
        """post data to api endpoint"""
        config = self.read_config()
        auth = (config["username"], config["password"])
        response = requests.post(config["url"], json=self.data, auth=auth)
        if not response.ok:
            print(response.text)

    def read_config(self):
        """read config file"""
        # build path
        root_folder = path.dirname(sys.argv[0])
        if root_folder == '/sbin':
            # running interactive
            config_path = 'config.json'
        else:
            config_path = path.join(root_folder, 'config.json')

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.loads(f.read())

            return config


if __name__ == "__main__":
    sensor = PiSensor()
    sensor.get_data()
    print(sensor.data)
    sensor.send_data()
