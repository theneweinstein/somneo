from homeassistant import config_entries
import ipaddress
import re
import voluptuous as vol
from .const import DOMAIN, CONF_HOST, CONF_NAME, DEFAULT_NAME

import pysomneo

def host_valid(host):
    """Return True if hostname or IP address is valid."""
    try:
        if ipaddress.ip_address(host).version == (4 or 6):
            return True
    except ValueError:
        disallowed = re.compile(r"[^a-zA-z\d\-]")
        return all(x and not disallowed.search(x) for x in host.split("."))

      
class SmartSleepConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""
    def __init__(self):
        """Initialize."""
        self.host = None
        self.name = None

    async def async_step_user(self, info):
        """Handle the initial step."""
        errors = {}

        if info is not None:
            if host_valid(info[CONF_HOST]):
                return self.async_create_entry(title="SmartSleep", data=info)

            errors[CONF_HOST] = "invalid_host"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_HOST): str, vol.Optional(CONF_NAME, default=DEFAULT_NAME): str})
        )

    async def async_step_import(self, import_data=None):
        """Handle configuration by yaml file."""

        if host_valid(import_data[CONF_HOST]):
            return self.async_create_entry(title='SmartSleep', data=import_data)
