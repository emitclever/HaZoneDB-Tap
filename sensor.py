from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities
):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = []

    for monitor_id in coordinator.data.keys():
        sensors.append(ZMScoreSensor(coordinator, monitor_id))

    async_add_entities(sensors, update_before_add=True)

class ZMScoreSensor(Entity):
    """Sensor for the latest 5-min bucket's TotScore."""

    def __init__(self, coordinator, monitor_id):
        self.coordinator = coordinator
        self.monitor_id = monitor_id

    @property
    def unique_id(self):
        return f"{DOMAIN}_score_{self.monitor_id}"

    @property
    def name(self):
        nm = self.coordinator.data[self.monitor_id]["name"]
        return f"ZoneMinder {nm} Total Score"

    @property
    def state(self):
        return self.coordinator.data[self.monitor_id]["latest_score"]

    @property
    def extra_state_attributes(self):
        info = self.coordinator.data[self.monitor_id]
        return {
            "bins": info["bins"],
            "latest_interval": info["latest_interval"],
        }

    async def async_update(self):
        await self.coordinator.async_request_refresh()




