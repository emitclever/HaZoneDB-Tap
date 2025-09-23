# custom_components/zoneminder_db/options_flow.py

import voluptuous as vol

from homeassistant import config_entries

from .const import (
    DOMAIN,
    CONF_POLL_INTERVAL,
    CONF_LOOKBACK_WINDOW,
    CONF_BIN_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_LOOKBACK_WINDOW,
    DEFAULT_BIN_INTERVAL,
)


class ZMOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle changes to ZoneMinder DB integration options."""

    def __init__(self, entry: config_entries.ConfigEntry):
        # Do NOT assign to self.config_entry (deprecated).
        # Instead keep your own reference and pull options from it.
        self.entry = entry
        self.options = dict(entry.options) if entry.options else {}

    async def async_step_init(self, user_input=None):
        """Display and handle the options form."""
        if user_input is not None:
            # Merge existing options with any new values
            updated = {**self.options, **user_input}
            return self.async_create_entry(title=self.entry.title, data=updated)

        # Build the form schema with defaults from existing options or CONST defaults
        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_POLL_INTERVAL,
                    default=self.options.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL),
                ): int,
                vol.Optional(
                    CONF_LOOKBACK_WINDOW,
                    default=self.options.get(CONF_LOOKBACK_WINDOW, DEFAULT_LOOKBACK_WINDOW),
                ): int,
                vol.Optional(
                    CONF_BIN_INTERVAL,
                    default=self.options.get(CONF_BIN_INTERVAL, DEFAULT_BIN_INTERVAL),
                ): int,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
