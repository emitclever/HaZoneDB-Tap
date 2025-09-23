import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_DB_HOST,
    CONF_DB_PORT,
    CONF_DB_NAME,
    CONF_DB_USER,
    CONF_DB_PASSWORD,
    CONF_POLL_INTERVAL,
    CONF_LOOKBACK_WINDOW,
    CONF_BIN_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_LOOKBACK_WINDOW,
    DEFAULT_BIN_INTERVAL,
)
from .options_flow import ZMOptionsFlowHandler

class ZMConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_DB_HOST], data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_DB_HOST, default="localhost"): str,
            vol.Required(CONF_DB_PORT, default=3306): int,
            vol.Required(CONF_DB_NAME, default="zm"): str,
            vol.Required(CONF_DB_USER, default="root"): str,
            vol.Required(CONF_DB_PASSWORD, default=""): str,
            vol.Optional(CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL): int,
            vol.Optional(CONF_LOOKBACK_WINDOW, default=DEFAULT_LOOKBACK_WINDOW): int,
            vol.Optional(CONF_BIN_INTERVAL, default=DEFAULT_BIN_INTERVAL): int,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ZMOptionsFlowHandler(config_entry)


