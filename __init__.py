import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .coordinator import ZMCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor", "binary_sensor"]

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    conf = {**entry.data, **entry.options}
    coordinator = ZMCoordinator(hass, conf)
    try:
        await coordinator.async_refresh()
    except Exception as err:
        _LOGGER.error("Initial DB connection failed: %s", err)
        return False

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
