import voluptuous as vol
from homeassistant import config_entries

from .const import (
    CONF_POLL_INTERVAL,
    CONF_LOOKBACK_WINDOW,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_LOOKBACK_WINDOW,
)

class ZMOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input:
            return self.async_create_entry(data=user_input)

        current = self.config_entry.options
        schema = vol.Schema({
            vol.Optional(
                CONF_POLL_INTERVAL,
                default=current.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)
            ): int,
            vol.Optional(
                CONF_LOOKBACK_WINDOW,
                default=current.get(CONF_LOOKBACK_WINDOW, DEFAULT_LOOKBACK_WINDOW)
            ): int,
        })

        return self.async_show_form(step_id="init", data_schema=schema)

