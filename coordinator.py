import mysql.connector
import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_DB_HOST,
    CONF_DB_PORT,
    CONF_DB_NAME,
    CONF_DB_USER,
    CONF_DB_PASSWORD,
    CONF_POLL_INTERVAL,
    CONF_LOOKBACK_WINDOW,
)

_LOGGER = logging.getLogger(__name__)

class ZMCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, config):
        interval = config.get(CONF_POLL_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            name="zoneminder_db",
            update_interval=timedelta(seconds=interval),
        )
        self.config = config

    async def _async_update_data(self):
        lookback = self.config.get(CONF_LOOKBACK_WINDOW)

        def fetch():
            conn = mysql.connector.connect(
                host=self.config[CONF_DB_HOST],
                port=self.config[CONF_DB_PORT],
                database=self.config[CONF_DB_NAME],
                user=self.config[CONF_DB_USER],
                password=self.config[CONF_DB_PASSWORD],
            )
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT Id, Name FROM Monitors")
            monitors = cursor.fetchall()

            cursor.execute(f"""
                SELECT
                  MonitorId,
                  COUNT(*)            AS count,
                  MAX(StartDateTime)  AS last_start
                FROM Events
                WHERE StartDateTime > NOW() - INTERVAL {lookback} MINUTE
                GROUP BY MonitorId
            """)
            # now each row has both count and last_start
            rows = cursor.fetchall()
            events = {
                row["MonitorId"]: {
                    "count": row["count"],
                    "last_start": row["last_start"],
                }
                for row in rows
            }


            cursor.close()
            conn.close()

            # ensure every monitor has a default structure
            return {
                m["Id"]: {
                    "name": m["Name"],
                    "count":      events.get(m["Id"], {}).get("count", 0),
                    "last_start": events.get(m["Id"], {}).get("last_start"),
                }
                for m in monitors
            }

        try:
            return await self.hass.async_add_executor_job(fetch)
        except Exception as err:
            raise UpdateFailed(f"Database polling failed: {err}") from err




