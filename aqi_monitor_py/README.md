# Python Sensor Application
Updated script running on a RaspberryPi. Pure python implementation.

## Install libraries
```
pip install -r requirements.txt
```

# Install service
```bash
sudo cp aqi_monitor_py/service/sensor.* /etc/systemd/system
sudo systemctl enable --now sensor.timer
```
