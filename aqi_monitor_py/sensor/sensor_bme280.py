"""interact with temperature sensor"""
# pylint: disable=import-error

import smbus2
import bme280


class BmeSensor:
    """interact with BME280 sensor on pi"""

    PORT = 1
    ADDRESS = 0x76

    def __init__(self):
        self.data = False

    def collect(self):
        """collect"""
        print("collect data from bme280")
        self.get_data()
        temperature_values = self.format_data()

        return temperature_values

    def get_data(self):
        """read data from sensor"""
        bus = smbus2.SMBus(self.PORT)
        calibration_params = bme280.load_calibration_params(bus, self.ADDRESS)
        self.data = bme280.sample(bus, self.ADDRESS, calibration_params)

    def format_data(self):
        """build dict to send"""
        temperature_values = {
            "temperature": round(self.data.temperature, 2),
            "pressure": round(self.data.pressure),
            "humidity": round(self.data.humidity, 2),
        }

        return temperature_values
