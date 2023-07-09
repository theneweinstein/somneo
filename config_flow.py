from __future__ import annotations

import ipaddress
import re
import logging
from typing import Any
from urllib.parse import urlparse

from homeassistant.components.ssdp import SsdpServiceInfo
import voluptuous as vol
from contextlib import suppress

from pysomneo import Somneo

from homeassistant import config_entries, exceptions
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, DEFAULT_NAME, CONF_SESSION

_LOGGER = logging.getLogger(__name__)

def host_valid(host) -> bool:
    """Return True if hostname or IP address is valid."""
    with suppress(ValueError):
        if ipaddress.ip_address(host).version in [4, 6]:
            return True
    disallowed = re.compile(r"[^a-zA-Z\d\-]")
    return all(x and not disallowed.search(x) for x in host.split("."))

def _base_schema(discovery_info: SsdpServiceInfo | None) -> vol.Schema:
    """Generate base schema for gateways."""
    base_schema = vol.Schema({vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,})

    if not discovery_info:
        base_schema = base_schema.extend(
            {
                vol.Required(CONF_HOST): str,
            }
        )

    return base_schema

class SomneoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""

    VERSION = 3

    discovery_info: SsdpServiceInfo | None = None
    host: str | None = None
    name: str = DEFAULT_NAME
    dev_info: dict | None = None

    async def get_device_info(self):
        """Get device info"""
        somneo = Somneo(self.host)
        dev_info = await self.hass.async_add_executor_job(somneo.get_device_info)

        return dev_info

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> SomneoOptionsFlow:
        """Thermosmart options callback."""
        return SomneoOptionsFlow(config_entry)

    async def async_step_ssdp(self, discovery_info: SsdpServiceInfo) -> FlowResult:
        """Prepare configuration for a discovered Somneo."""
        _LOGGER.debug("SSDP user_input: %s", discovery_info)

        self.discovery_info = discovery_info

        serial_number = discovery_info.ssdp_udn.split('-')[-1]
        self.host = urlparse(
            discovery_info.ssdp_location
        ).hostname

        _LOGGER.debug(self.host)

        await self.async_set_unique_id(serial_number)

        self._abort_if_unique_id_configured()

        _LOGGER.debug("It is not aborted.")

        return await self.async_step_user()


    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if self.discovery_info:
                user_input[CONF_HOST] = self.host

            if host_valid(user_input[CONF_HOST]):
                try:
                    user_input['dev_info'] = await self.get_device_info()
                except Exception as ex:
                    errors["base"] = str(ex)
                else:
                    await self.async_set_unique_id(user_input['dev_info']['serial'])
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_base_schema(self.discovery_info),
            errors=errors
        )

class SomneoOptionsFlow(config_entries.OptionsFlow):
    """Config flow options for Somneo"""

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialze the Somneo options flow."""
        self.entry = entry
        self.use_session = self.entry.options.get(CONF_SESSION, True)

    async def async_step_init(self, _user_input=None):
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Process user input."""
        if user_input is not None:
            return self.async_create_entry(title = "Somneo", data = user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_SESSION, default = self.use_session): bool,
                }
            )
        )

class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""
