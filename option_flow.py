import voluptuous as vol

from homeassistant import config_entries

from .const import (
    CONF_POLL_INTERVAL,
    CONF_LOOKBACK_WINDOW,
    CONF_BIN_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_LOOKBACK_WINDOW,
    DEFAULT_BIN_INTERVAL,
)

class ZMOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        data = self.config_entry.options or {}
        if user_input is not None:
            return self.async_create_entry(title="", data={**data, **user_input})

        schema = vol.Schema({
            vol.Optional(
                CONF_POLL_INTERVAL,
                default=data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)
            ): int,
            vol.Optional(
                CONF_LOOKBACK_WINDOW,
                default=data.get(CONF_LOOKBACK_WINDOW, DEFAULT_LOOKBACK_WINDOW)
            ): int,
            vol.Optional(
                CONF_BIN_INTERVAL,
                default=data.get(CONF_BIN_INTERVAL, DEFAULT_BIN_INTERVAL)
            ): int,
        })

        return self.async_show_form(step_id="init", data_schema=schema, errors={})



