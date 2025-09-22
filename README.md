ZoneMinder DB Custom Integration for Home Assistant

A lightweight Home Assistant integration that reads event counts and last-start datetimes straight from your ZoneMinder MariaDB. 
Perfect for dashboards, automations.

custom_components/zoneminder_db/
    ── __init__.py         # Integration setup & platform forwarding
    ── manifest.json       # Integration metadata & dependencies
    ── const.py            # Configuration keys & defaults
    ── config_flow.py      # UI-driven setup flow
    ── options_flow.py     # In-UI options (poll interval, lookback)
    ── coordinator.py      # DataUpdateCoordinator => DB polling
    ── sensor.py           # Event count & last-start timestamp sensors
    ── binary_sensor.py    # “Is active?” binary sensors

1. First you have to setup DB to listen on all interfaces if not localhost. Mine is a separate server
    sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
    bind-address            = 0.0.0.0
    # skip-networking      = 0    ← ensure this line is commented out
   sudo systemctl restart mariadb
   netstat -tunlp | grep 3306
   You should see 0.0.0.0:3306 or your LAN IP there.

   Grant your HA host user rights
     sudo mysql
    GRANT SELECT
    ON zm.*
    TO 'zmuser'@'HA_IP'
    IDENTIFIED BY 'zmpass';
    FLUSH PRIVILEGES;
  (Optional) If you want to allow any host, use % instead of HA_IP:
    GRANT SELECT ON zm.* TO 'zmuser'@'%' IDENTIFIED BY 'zmpass';
    FLUSH PRIVILEGES;

  Adjust your firewall if needed
  example
  GRANT SELECT
    ON zm.*
    TO 'zmuser'@'192.168.1.100'
    IDENTIFIED BY 'zmpass';
  FLUSH PRIVILEGES;
  
  OR
  
  GRANT SELECT
  ON zm.*
  TO 'zmuser'@'192.168.1.%'
  IDENTIFIED BY 'zmpass';
  FLUSH PRIVILEGES;

   
3. Create/Copy the zoneminder_db folder in to your Home Assistant custom_components/ directory.

4. (Optional) Add this to your configuration.yaml (optional – can also do UI setup):
zoneminder_db:
  host: 192.168.1.50
  port: 3306
  database: zm
  username: zmuser
  password: secure_password
  poll_interval: 60          # seconds
  lookback_window: 10        # minutes

4.Restart Home Assistant.
5.Go to Settings → Devices & Services → Add Integration → ZoneMinder DB and fill in your DB details.

Contributing

    Fork the repo, create a feature branch, submit pull requests.
    Please maintain PEP8 compliance and add tests for new features.
    Drop issues or PRs for schema changes, new sensors, or performance tweaks.
