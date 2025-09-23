# custom_components/zoneminder_db/sensor.py

from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up all ZoneMinder sensors for each monitor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for monitor_id in coordinator.data.keys():
        entities.append(ZMRollingCountSensor(coordinator, monitor_id))
        entities.append(ZMLastStartSensor(coordinator, monitor_id))
        entities.append(ZMInProgressSensor(coordinator, monitor_id))
        entities.append(ZMScoreSensor(coordinator, monitor_id))

    async_add_entities(entities, update_before_add=True)


class ZMRollingCountSensor(Entity):
    """Number of 10-minute chunks in the lookback window."""

    def __init__(self, coordinator, monitor_id):
        self.coordinator = coordinator
        self.monitor_id = monitor_id

    @property
    def unique_id(self):
        return f"{DOMAIN}_rolling_count_{self.monitor_id}"

    @property
    def name(self):
        name = self.coordinator.data[self.monitor_id]["name"]
        return f"ZoneMinder {name} Rolling Count"

    @property
    def state(self):
        return self.coordinator.data[self.monitor_id]["rolling_count"]

    @property
    def extra_state_attributes(self):
        last = self.coordinator.data[self.monitor_id]["last_start"]
        return {"last_event_start": last}

    async def async_update(self):
        await self.coordinator.async_request_refresh()


class ZMLastStartSensor(Entity):
    """Timestamp of the most recent chunk start."""

    def __init__(self, coordinator, monitor_id):
        self.coordinator = coordinator
        self.monitor_id = monitor_id

    @property
    def unique_id(self):
        return f"{DOMAIN}_last_start_{self.monitor_id}"

    @property
    def name(self):
        name = self.coordinator.data[self.monitor_id]["name"]
        return f"ZoneMinder {name} Last Start"

    @property
    def state(self):
        return self.coordinator.data[self.monitor_id]["last_start"]

    @property
    def device_class(self):
        return "timestamp"

    async def async_update(self):
        await self.coordinator.async_request_refresh()
class ZMInProgressSensor(Entity):
    """Number of recordings currently in progress (0 or 1)."""

    def __init__(self, coordinator, monitor_id):
        self.coordinator = coordinator
        self.monitor_id = monitor_id

    @property
    def unique_id(self):
        return f"{DOMAIN}_active_count_{self.monitor_id}"

    @property
    def name(self):
        name = self.coordinator.data[self.monitor_id]["name"]
        return f"ZoneMinder {name} Active Count"

    @property
    def state(self):
        return self.coordinator.data[self.monitor_id]["active_count"]

    async def async_update(self):
        await self.coordinator.async_request_refresh()

class ZMScoreSensor(Entity):
    """Latest 5-minute TotScore and historic bins."""

    def __init__(self, coordinator, monitor_id):
        self.coordinator = coordinator
        self.monitor_id = monitor_id

    @property
    def unique_id(self):
        return f"{DOMAIN}_total_score_{self.monitor_id}"

    @property
    def name(self):
        name = self.coordinator.data[self.monitor_id]["name"]
        return f"ZoneMinder {name} Total Score"

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


