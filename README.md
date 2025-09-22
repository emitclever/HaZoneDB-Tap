# ZoneMinder DB Custom Integration for Home Assistant
It is an atempt to play with custom_integration still in infancy ... there are maybe other solutions more advanced, I just wanted to pull out from zoneminder database for home assistant
<img width="1033" height="258" alt="image" src="https://github.com/user-attachments/assets/4456e3d0-6bd7-4f0b-a7b4-fd3ffe8b11df" />

A lightweight Home Assistant integration that reads event counts and last-start datetimes straight from your ZoneMinder MariaDB. Perfect for dashboards and automations.

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
  poll_interval: 60          # seconds
  lookback_window: 10        # minutes

Restart Home Assistant.

Add Integration via UI

Go to: Settings → Devices & Services → Add Integration → ZoneMinder DB and fill in your DB details.Copy
Contributing
Fork the repo, create a feature branch, and submit pull requests.
Please maintain PEP8 compliance and add tests for new features.
Submit issues or PRs for schema changes, new sensors, or performance tweaks.
Feel free to reach out for support or enhancements!
