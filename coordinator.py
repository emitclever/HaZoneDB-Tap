# custom_components/zoneminder_db/coordinator.py

import logging
from datetime import timedelta

import mysql.connector
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_DB_HOST,
    CONF_DB_PORT,
    CONF_DB_NAME,
    CONF_DB_USER,
    CONF_DB_PASSWORD,
    CONF_POLL_INTERVAL,
    CONF_LOOKBACK_WINDOW,
    CONF_BIN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class ZMCoordinator(DataUpdateCoordinator):
    """Periodically polls ZoneMinder’s Events table, grouping into time bins."""

    def __init__(self, hass, config):
        interval = config[CONF_POLL_INTERVAL]
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=interval),
        )
        self.config = config

    async def _async_update_data(self):
        lookback = self.config[CONF_LOOKBACK_WINDOW]
        bin_int  = self.config[CONF_BIN_INTERVAL]

        def fetch():
            conn = mysql.connector.connect(
                host=self.config[CONF_DB_HOST],
                port=self.config[CONF_DB_PORT],
                user=self.config[CONF_DB_USER],
                password=self.config[CONF_DB_PASSWORD],
                database=self.config[CONF_DB_NAME],
            )
            try:
                cursor = conn.cursor(dictionary=True)

                # 1) Fetch all monitors
                cursor.execute("SELECT `Id`, `Name` FROM `Monitors`")
                monitors = cursor.fetchall()

                # 2) Query 5-minute bins for the lookback window
                cursor.execute(f"""
                    SELECT
                      `MonitorId`,
                      CONCAT(
                        DATE_FORMAT(StartDateTime, '%Y-%m-%d %H:'),
                        LPAD(FLOOR(MINUTE(StartDateTime)/{bin_int})*{bin_int}, 2, '0'),
                        ':00'
                      ) AS interval_start,
                      SUM(`TotScore`)    AS total_score,
                      SUM(`AlarmFrames`) AS alarm_frames
                    FROM `Events`
                    WHERE StartDateTime > NOW() - INTERVAL {lookback} MINUTE
                    GROUP BY MonitorId, interval_start
                    ORDER BY MonitorId, interval_start;
                """)
                rows = cursor.fetchall()

                # 3) Organize data per monitor, casting Decimal → int
                data = {
                    m["Id"]: {"name": m["Name"], "bins": []}
                    for m in monitors
                }

                for row in rows:
                    mid = row["MonitorId"]
                    data[mid]["bins"].append({
                        "interval_start": row["interval_start"],
                        "total_score":    int(row["total_score"]),
                        "alarm_frames":   int(row["alarm_frames"]),
                    })

                # 4) Derive latest bucket metrics
                for mid, info in data.items():
                    bins = info["bins"]
                    if bins:
                        last = bins[-1]
                        info["latest_score"]    = last["total_score"]
                        info["latest_interval"] = last["interval_start"]
                    else:
                        info["latest_score"]    = 0
                        info["latest_interval"] = None

                return data

            finally:
                cursor.close()
                conn.close()

        try:
            return await self.hass.async_add_executor_job(fetch)
        except Exception as err:
            _LOGGER.error("Database polling failed: %s", err)
            raise UpdateFailed(err)

