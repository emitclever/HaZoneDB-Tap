import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .coordinator import ZMCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor"]

async def async_setup(hass: HomeAssistant, config: dict):
    """Nothing to do; we’re config-flow only."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Zoneminder-DB from a config entry."""
    conf = {**entry.data, **entry.options}
    coordinator = ZMCoordinator(hass, conf)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        _LOGGER.error("Initial ZoneMinder DB connection failed")
        return False

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Forward setup to both platforms at once
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload Zoneminder-DB config entry."""
    # Forward unload to both platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
