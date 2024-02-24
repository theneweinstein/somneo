"""Config flow for Somneo."""
from __future__ import annotations

import ipaddress
import logging
import re
from contextlib import suppress
from typing import Any
from urllib.parse import urlparse

import voluptuous as vol
from homeassistant import config_entries, exceptions
from homeassistant.components.ssdp import SsdpServiceInfo
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from pysomneo import Somneo

from .const import CONF_SESSION, DEFAULT_NAME, DOMAIN

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
    base_schema = vol.Schema(
        {
            vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
        }
    )

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
        """Get device info."""
        somneo = Somneo(self.host)
        dev_info = await self.hass.async_add_executor_job(somneo.get_device_info)

        return dev_info

    async def async_step_ssdp(self, discovery_info: SsdpServiceInfo) -> FlowResult:
        """Prepare configuration for a discovered Somneo."""
        _LOGGER.debug("SSDP discovery: %s", discovery_info)

        self.discovery_info = discovery_info

        serial_number = discovery_info.upnp["cppId"]
        self.host = urlparse(discovery_info.ssdp_location).hostname

        await self.async_set_unique_id(serial_number)

        self._abort_if_unique_id_configured(updates={CONF_HOST: self.host})

        return await self.async_step_user()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        _LOGGER.debug(user_input)

        if user_input is not None:
            if self.discovery_info:
                _LOGGER.debug("Discovery info found.")
                user_input[CONF_HOST] = self.host
            else:
                self.host = user_input[CONF_HOST]

            if host_valid(user_input[CONF_HOST]):
                try:
                    user_input["dev_info"] = await self.get_device_info()
                except Exception as ex:
                    errors["base"] = str(ex)
                else:
                    await self.async_set_unique_id(user_input["dev_info"]["serial"])
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=user_input[CONF_NAME], data=user_input
                    )

        return self.async_show_form(
            step_id="user", data_schema=_base_schema(self.discovery_info), errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return SomneoOptionsFlow(config_entry)

class SomneoOptionsFlow(config_entries.OptionsFlow):
    """Config flow options for Somneo"""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialze the Somneo options flow."""
        self.config_entry = config_entry

    async def async_step_init(
            self,
            user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title = "Somneo", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SESSION,
                        default=self.config_entry.options.get(CONF_SESSION, True)
                    ): bool,
                }
            )
        )

class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""
