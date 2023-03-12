# Python Sensor Application
Updated script running on a RaspberryPi. Pure python implementation.

## Pi Setup
Enable *I2C1*: `sudo raspi-config` > *Interface Options* > *I2C*

## Install libraries
```
sudo apt install git python3-pip
```

```
pip3 install -r requirements.txt
```

Setup *config.json*

# Install service
```bash
sudo cp aqi_monitor/aqi_monitor_py/service/sensor.* /etc/systemd/system
sudo systemctl enable --now sensor.timer
```

Watch service logs for errors:
```
journalctl -u sensor -f
```
