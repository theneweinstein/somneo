from __future__ import annotations

import ipaddress
import re
from typing import Any
import voluptuous as vol
from contextlib import suppress

from pysomneo import Somneo

from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, DEFAULT_NAME, CONF_SESSION

def host_valid(host) -> bool:
    """Return True if hostname or IP address is valid."""
    with suppress(ValueError):
        if ipaddress.ip_address(host).version in [4, 6]:
            return True
    disallowed = re.compile(r"[^a-zA-Z\d\-]")
    return all(x and not disallowed.search(x) for x in host.split("."))

class SomneoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""

    VERSION = 2

    def __init__(self) -> None:
        """Initialize."""
        self.somneo: Somneo | None = None
        self.host: str | None = None
        self.use_session: bool = True
        self.name: str = DEFAULT_NAME
        self.dev_info: dict | None = None

    async def init_device(self) -> None:
        """Initialize Somneo device."""
        assert self.somneo is not None
        self.dev_info = await self.hass.async_add_executor_job(self.somneo.get_device_info)

        await self.async_set_unique_id(self.dev_info['serial'].lower())
        self._abort_if_unique_id_configured()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if host_valid(user_input[CONF_HOST]):
                try:
                    self.host = user_input[CONF_HOST]
                    self.name = user_input[CONF_NAME]
                    self.use_session = user_input[CONF_SESSION]
                    self.somneo = Somneo(self.host)
                    await self.init_device()
                except Exception as ex:
                    errors["base"] = str(ex)
                else:
                    user_input['dev_info'] = self.dev_info
                    return self.async_create_entry(title=self.name, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_SESSION, default=True): bool,
                }
            ),
            errors=errors
        )

class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""
