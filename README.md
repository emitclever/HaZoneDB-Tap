# ZoneMinder DB Custom Integration for Home Assistant
It is an atempt to play with custom_integration still in infancy ... there are maybe other solutions more advanced, I just wanted to pull out from zoneminder database for home assistant

A lightweight Home Assistant integration that reads event counts and last-start datetimes straight from your ZoneMinder MariaDB. Perfect for dashboards and automations.
<img width="506" height="507" alt="image" src="https://github.com/user-attachments/assets/de21b221-5526-4ef9-a223-03713b0ae2c3" />

## Integration Files

```plaintext
custom_components/zoneminder_db/
├── __init__.py         # Integration setup & platform forwarding
├── manifest.json       # Integration metadata & dependencies
├── const.py            # Configuration keys & defaults
├── config_flow.py      # UI-driven setup flow
├── options_flow.py     # In-UI options (poll interval, lookback)
├── coordinator.py      # DataUpdateCoordinator => DB polling
├── sensor.py           # Event count & last-start timestamp sensors
└── binary_sensor.py    # “Is active?” binary sensors

Requirements
    Home Assistant >= 0.XX
    Python package: mysql-connector-python
    A ZoneMinder MariaDB accessible from your HA host

Setup Instructions
Configure Your Database

Edit the MariaDB Configuration: Ensure your DB is set to listen on all interfaces if it's not hosted on the same machine.

sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf

Update the following lines:

bind-address = 0.0.0.0
# skip-networking = 0    ← ensure this line is commented out
Restart MariaDB and check connections:

sudo systemctl restart mariadb
netstat -tunlp | grep 3306

Grant User Rights to Home Assistant Host:

sudo mysql
GRANT SELECT
ON zm.*
TO 'zmuser'@'HA_IP'
IDENTIFIED BY 'zmpass';
FLUSH PRIVILEGES;

(Optional) Allow any host by using % instead of HA_IP:CopyCopy

GRANT SELECT ON zm.* TO 'zmuser'@'%' IDENTIFIED BY 'zmpass';
FLUSH PRIVILEGES;

Adjust your firewall if needed.

Example Grants:

GRANT SELECT
ON zm.*
TO 'zmuser'@'192.168.1.100'
IDENTIFIED BY 'zmpass';
FLUSH PRIVILEGES;

GRANT SELECT
ON zm.*
TO 'zmuser'@'192.168.1.%'
IDENTIFIED BY 'zmpass';
FLUSH PRIVILEGES;

Installation

Create/Copy the zoneminder_db folder into your Home Assistant custom_components/ directory.CopyCopy
Configuration

(Optional) Add the following to your configuration.yaml:
zoneminder_db:
  host: 192.168.1.50
  port: 3306
  database: zm
  username: zmuser
  password: secure_password
  poll_interval: 60       # seconds
  lookback_window: 60     # minutes
  bin_interval: 5         # minutes for TotScore aggregation

Restart Home Assistant.

Add Integration via UI

Go to: Settings → Devices & Services → Add Integration → ZoneMinder DB and fill in your DB details.Copy

This integration now creates for each ZoneMinder monitor:
sensor.zoneminder_<monitor_id>_rolling_count
• Description – Rolling count of video‐chunk starts in your configured lookback window (default 60 min).
• State – Integer number of 10-minute chunks that began in that window.
• Attributes – last_event_start: ISO timestamp of the most recent chunk start.
• Role – Gives you a quick metric of how often recordings have started recently.

sensor.zoneminder_<monitor_id>_last_start
• Description – Exact timestamp of the most recent recording‐chunk StartDateTime.
• State – ISO-formatted datetime string (device_class “timestamp”). • Role – Lets you know exactly when the last video chunk began.

sensor.zoneminder_<monitor_id>_active_count
• Description – Number of recording events currently in progress (EndDateTime still null or > now).
• State – Integer, usually 0 or 1.
• Role – Indicates live recording status for automations or dashboards.

sensor.zoneminder_<monitor_id>_total_score
• Description – Sum of motion‐analysis scores (TotScore) for the latest 5-min interval.
• State – Integer total_score of the newest bin.
• Attributes – bins: List of all 5-min buckets in your lookback window, each with
• interval_start (string)
• total_score (int)
• alarm_frames (int) – latest_interval: ISO string of the current 5-min bucket.
• Role – Provides a time-series view of activity intensity you can chart or inspect.

binary_sensor.zoneminder_<monitor_id>_alarm
• Description – Alarm flag toggled on whenever the latest 5-min bucket’s total_score > 0.
• State – on/off.
• Role – Simple motion-detected switch you can use directly in triggers or alerts.


Contributing
Fork the repo, create a feature branch, and submit pull requests.
Please maintain PEP8 compliance and add tests for new features.
Submit issues or PRs for schema changes, new sensors, or performance tweaks.
Feel free to reach out for support or enhancements!
