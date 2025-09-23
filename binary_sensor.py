# custom_components/zoneminder_db/binary_sensor.py

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Set up ZoneMinder alarm binary sensor for each monitor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    devices = []

    for monitor_id in coordinator.data.keys():
        devices.append(ZMAlarmBinarySensor(coordinator, monitor_id))

    async_add_entities(devices, update_before_add=True)


class ZMAlarmBinarySensor(BinarySensorEntity):
    """Turns on when the latest TotScore > 0."""

    def __init__(self, coordinator, monitor_id):
        self.coordinator = coordinator
        self.monitor_id = monitor_id

    @property
    def unique_id(self):
        return f"{DOMAIN}_alarm_{self.monitor_id}"

    @property
    def name(self):
        name = self.coordinator.data[self.monitor_id]["name"]
        return f"ZoneMinder {name} Alarm"

    @property
    def is_on(self):
        return self.coordinator.data[self.monitor_id]["latest_score"] > 0

    async def async_update(self):
        await self.coordinator.async_request_refresh()


