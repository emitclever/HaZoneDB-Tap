from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        ZMEventActiveSensor(coordinator, monitor_id)
        for monitor_id in coordinator.data.keys()
    ]
    async_add_entities(entities, update_before_add=True)

class ZMEventActiveSensor(BinarySensorEntity):
    def __init__(self, coordinator, monitor_id):
        self.coordinator = coordinator
        self.monitor_id = monitor_id

    @property
    def name(self):
        data = self.coordinator.data[self.monitor_id]
        return f"ZoneMinder {data['name']} Active"

    @property
    def unique_id(self):
        return f"{DOMAIN}_active_{self.monitor_id}"

    @property
    def is_on(self):
        return self.coordinator.data[self.monitor_id]["count"] > 0

    async def async_update(self):
        await self.coordinator.async_request_refresh()
