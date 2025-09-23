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


def _safe_int(val):
    """Convert a value to int, returning 0 if it's None or invalid."""
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


class ZMCoordinator(DataUpdateCoordinator):
    """Poll ZoneMinder Events for bins, rolling counts, last start, and active."""

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

                # 1) Fetch monitors
                cursor.execute("SELECT `Id`, `Name` FROM `Monitors`")
                monitors = cursor.fetchall()

                # Initialize data structure
                data = {
                    m["Id"]: {
                        "name":             m["Name"],
                        "bins":             [],
                        "rolling_count":    0,
                        "last_start":       None,
                        "active_count":     0,
                        "latest_score":     0,
                        "latest_interval":  None,
                    }
                    for m in monitors
                }

                # 2) 5-minute bins for TotScore & AlarmFrames
                cursor.execute(f"""
                    SELECT
                      MonitorId,
                      CONCAT(
                        DATE_FORMAT(StartDateTime, '%Y-%m-%d %H:'),
                        LPAD(FLOOR(MINUTE(StartDateTime)/{bin_int})*{bin_int}, 2, '0'),
                        ':00'
                      ) AS interval_start,
                      SUM(TotScore)    AS total_score,
                      SUM(AlarmFrames) AS alarm_frames
                    FROM Events
                    WHERE StartDateTime > NOW() - INTERVAL {lookback} MINUTE
                    GROUP BY MonitorId, interval_start
                    ORDER BY MonitorId, interval_start;
                """)
                for row in cursor.fetchall():
                    mid = row["MonitorId"]
                    data[mid]["bins"].append({
                        "interval_start": row["interval_start"],
                        "total_score":    _safe_int(row["total_score"]),
                        "alarm_frames":   _safe_int(row["alarm_frames"]),
                    })

                # 3) Rolling count & last start in lookback window
                cursor.execute(f"""
                    SELECT
                      MonitorId,
                      COUNT(*)           AS rolling_count,
                      MAX(StartDateTime) AS last_start
                    FROM Events
                    WHERE StartDateTime > NOW() - INTERVAL {lookback} MINUTE
                    GROUP BY MonitorId;
                """)
                for row in cursor.fetchall():
                    mid = row["MonitorId"]
                    data[mid]["rolling_count"] = _safe_int(row["rolling_count"])
                    data[mid]["last_start"]    = (
                        row["last_start"].isoformat() if row["last_start"] else None
                    )

                # 4) Active count: any event where score > 0 in this case
                cursor.execute(f"""
                    SELECT MonitorId, COUNT(CASE WHEN TotScore > 0 THEN 1 END) AS active_count
                    FROM Events
                    WHERE StartDateTime > NOW() - INTERVAL {lookback} MINUTE
                    GROUP BY MonitorId;
                """)
                for row in cursor.fetchall():
                    mid = row["MonitorId"]
                    data[mid]["active_count"] = _safe_int(row["active_count"])

                # 5) Derive latest bucket metrics
                for mid, info in data.items():
                    if info["bins"]:
                        last = info["bins"][-1]
                        info["latest_score"]    = last["total_score"]
                        info["latest_interval"] = last["interval_start"]

                return data

            finally:
                cursor.close()
                conn.close()

        try:
            return await self.hass.async_add_executor_job(fetch)
        except Exception as err:
            _LOGGER.error("Database polling failed: %s", err)
            raise UpdateFailed(err)
