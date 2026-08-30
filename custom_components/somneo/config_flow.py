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
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.service_info.ssdp import SsdpServiceInfo
from pysomneo import Somneo

from .const import DEFAULT_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)


def host_valid(host: str) -> bool:
    """Return True if hostname or IP address is valid."""
    with suppress(ValueError):
        if ipaddress.ip_address(host).version == 4:
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


def _reconfigure_schema() -> vol.Schema:
    """Generate a schema for reconfiguring an existing entry."""
    return vol.Schema(
        {
            vol.Required(CONF_HOST): str,
            vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
        }
    )


class SomneoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""

    VERSION = 4

    discovery_info: SsdpServiceInfo | None = None
    host: str | None = None
    name: str = DEFAULT_NAME

    async def get_device_info(self) -> dict:
        """Get device info."""
        somneo = Somneo(self.host)
        try:
            dev_info = await somneo.get_device_info()
        except Exception as ex:
            raise CannotConnect from ex

        return dev_info

    async def async_step_ssdp(self, discovery_info: SsdpServiceInfo) -> FlowResult:
        """Prepare configuration for a discovered Somneo."""
        _LOGGER.debug("SSDP discovery: %s", discovery_info)

        self.discovery_info = discovery_info

        serial_number = discovery_info.upnp["cppId"]
        self.host = urlparse(discovery_info.ssdp_location).hostname

        if not host_valid(self.host):
            return self.async_abort(reason="not_ipv4")

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
                    dev_info = await self.get_device_info()
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                else:
                    await self.async_set_unique_id(dev_info["serial"])
                    self._abort_if_unique_id_configured(
                        updates={CONF_HOST: user_input[CONF_HOST]}
                    )
                    return self.async_create_entry(
                        title=user_input[CONF_NAME],
                        data={
                            CONF_HOST: user_input[CONF_HOST],
                            CONF_NAME: user_input[CONF_NAME],
                        },
                    )

        return self.async_show_form(
            step_id="user", data_schema=_base_schema(self.discovery_info), errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle reconfiguration of an existing entry."""
        errors: dict[str, str] = {}
        reconfigure_entry = self._get_reconfigure_entry()

        if user_input is not None:
            self.host = user_input[CONF_HOST]
            if not host_valid(self.host):
                errors[CONF_HOST] = "invalid_host"
            else:
                try:
                    dev_info = await self.get_device_info()
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                else:
                    await self.async_set_unique_id(dev_info["serial"])
                    self._abort_if_unique_id_mismatch()
                    return self.async_update_reload_and_abort(
                        reconfigure_entry,
                        title=user_input[CONF_NAME],
                        data={
                            CONF_HOST: user_input[CONF_HOST],
                            CONF_NAME: user_input[CONF_NAME],
                        },
                    )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                _reconfigure_schema(),
                reconfigure_entry.data,
            ),
            errors=errors,
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""
