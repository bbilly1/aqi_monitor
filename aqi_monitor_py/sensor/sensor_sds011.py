"""interact with aqi and environment sensors on pi4"""
import os
from time import sleep
import simple_sds011  # pylint: disable=import-error


class SDS:
    """collect data from sds011 sensor"""

    def __init__(self):
        self.port = self.get_port()
        self.pm = simple_sds011.SDS011(self.port)

    def collect(self):
        """collect average values"""
        self.startup()
        pm_values = self.query_sensor()
        self.shutdown()

        return pm_values

    def get_port(self):
        """find tty port for sds sensor"""
        usbs = [i for i in os.listdir("/dev/") if i.startswith("ttyUSB")]
        if len(usbs) > 1:
            raise ValueError(f"too many ttyUSBs found: {usbs}")

        port = f"/dev/{usbs[0]}"

        return port

    def startup(self):
        """activate and set mode"""
        self.pm.active = 1
        sleep(0.5)
        self.pm.mode = simple_sds011.MODE_PASSIVE
        print("warm up sensor")
        sleep(20)

    def query_sensor(self):
        """query 15 times"""
        print("collect samples")
        pm25_sample = []
        pm10_sample = []

        for _ in range(15):
            response = self.pm.query()
            pm25, pm10 = response.get("value").values()

            pm25_sample.append(pm25)
            pm10_sample.append(pm10)

            sleep(1)

        pm25_avg = self.avg(pm25_sample)
        pm10_avg = self.avg(pm10_sample)

        pm_values = {
            "pm25": pm25_avg,
            "pm10": pm10_avg
        }

        return pm_values

    def shutdown(self):
        """deactivate"""
        self.pm.active = 0

    @staticmethod
    def avg(lst):
        """calc average of list"""
        return round(sum(lst) / len(lst), 1)
