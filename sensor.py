from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    # for each monitor, create both sensors
    for monitor_id in coordinator.data.keys():
        entities.append(ZMEventCountSensor(coordinator, monitor_id))
        entities.append(ZMLastStartSensor(coordinator, monitor_id))

    async_add_entities(entities, update_before_add=True)

class ZMEventCountSensor(Entity):
    def __init__(self, coordinator, monitor_id):
        self.coordinator = coordinator
        self.monitor_id = monitor_id

    @property
    def name(self):
        data = self.coordinator.data[self.monitor_id]
        return f"ZoneMinder {data['name']} Event Count"

    @property
    def unique_id(self):
        return f"{DOMAIN}_count_{self.monitor_id}"

    @property
    def state(self):
        return self.coordinator.data[self.monitor_id]["count"]

    @property
    def extra_state_attributes(self):
        last = self.coordinator.data[self.monitor_id]["last_start"]
        return {"last_event_start": last.isoformat() if last else None}

    async def async_update(self):
        await self.coordinator.async_request_refresh()

class ZMLastStartSensor(Entity):
    """Sensor to expose only the last event start datetime."""

    def __init__(self, coordinator, monitor_id):
        self.coordinator = coordinator
        self.monitor_id = monitor_id

    @property
    def name(self):
        data = self.coordinator.data[self.monitor_id]
        return f"ZoneMinder {data['name']} Last Event Start"

    @property
    def unique_id(self):
        return f"{DOMAIN}_laststart_{self.monitor_id}"

    @property
    def state(self):
        last = self.coordinator.data[self.monitor_id]["last_start"]
        # Home Assistant will parse ISO8601 strings as datetimes
        return last.isoformat() if last else None

    async def async_update(self):
        await self.coordinator.async_request_refresh()



