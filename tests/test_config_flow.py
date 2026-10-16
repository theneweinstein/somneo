"""Tests for the Somneo config flow."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.service_info.ssdp import (
    ATTR_UPNP_UDN,
    SsdpServiceInfo,
)

from custom_components.somneo.config_flow import host_valid
from custom_components.somneo.const import DOMAIN

from .common import HOST, NAME, SERIAL

MOCK_SSDP = SsdpServiceInfo(
    ssdp_st="urn:schemas-upnp-org:device:basic:1",
    ssdp_usn="mock-usn",
    ssdp_location=f"http://{HOST}:8080/",
    upnp={
        ATTR_UPNP_UDN: "uuid:1234",
        "cppId": SERIAL,
    },
)

DEVICE_INFO = {
    "manufacturer": "Philips",
    "model": "Wake-up Light",
    "modelnumber": "HF3650/01",
    "serial": SERIAL,
}


async def test_host_valid() -> None:
    """Test the host validity helper."""
    assert host_valid("192.168.1.1")
    assert host_valid("somneo.local")
    assert not host_valid("")
    assert not host_valid("not a valid host!")
    # Not an IPv4 address, but the fallback hostname check accepts it.
    assert host_valid("256.256.256.256")


async def test_form_flow_manual(hass: HomeAssistant) -> None:
    """Test the user step creates an entry with host and name."""
    with patch(
        "custom_components.somneo.config_flow.Somneo"
    ) as somneo_cls:
        somneo_cls.return_value.get_device_info = AsyncMock(
            return_value=dict(DEVICE_INFO)
        )
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: HOST, CONF_NAME: NAME},
        )
        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == NAME
        assert result["data"] == {CONF_HOST: HOST, CONF_NAME: NAME}
        assert result["context"]["unique_id"] == SERIAL


async def test_ssdp_flow_sets_cppid_unique_id(hass: HomeAssistant) -> None:
    """Test SSDP discovery uses the cppId as the stable unique id."""
    with patch(
        "custom_components.somneo.config_flow.Somneo"
    ) as somneo_cls:
        somneo_cls.return_value.get_device_info = AsyncMock(
            return_value=dict(DEVICE_INFO, serial="different-serial")
        )
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_SSDP},
            data=MOCK_SSDP,
        )
        assert result["type"] == FlowResultType.FORM

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_NAME: NAME},
        )
        assert result["type"] == FlowResultType.CREATE_ENTRY
        # The unique id must come from the discovered cppId, NOT the
        # device-reported serial.
        assert result["context"]["unique_id"] == SERIAL
        assert result["data"][CONF_HOST] == HOST


async def test_ssdp_flow_aborts_without_serial(hass: HomeAssistant) -> None:
    """Test SSDP discovery aborts when no cppId is present."""
    ssdp_no_serial = SsdpServiceInfo(
        ssdp_st="urn:schemas-upnp-org:device:basic:1",
        ssdp_usn="mock-usn",
        ssdp_location=f"http://{HOST}:8080/",
        upnp={ATTR_UPNP_UDN: "uuid:1234"},
    )
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_SSDP},
        data=ssdp_no_serial,
    )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "no_serial"


async def test_reconfigure_updates_entry(hass: HomeAssistant, config_entry) -> None:
    """Test the reconfigure step updates host/name on an existing entry."""
    with patch(
        "custom_components.somneo.config_flow.Somneo"
    ) as somneo_cls:
        somneo_cls.return_value.get_device_info = AsyncMock(
            return_value=dict(DEVICE_INFO)
        )
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_RECONFIGURE,
                "entry_id": config_entry.entry_id,
            },
        )
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "reconfigure"

        new_host = "192.168.1.200"
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: new_host, CONF_NAME: "Renamed"},
        )
        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "reconfigure_successful"

        entry = hass.config_entries.async_get_entry(config_entry.entry_id)
        assert entry is not None
        assert entry.data[CONF_HOST] == new_host
        assert entry.data[CONF_NAME] == "Renamed"


async def test_reconfigure_cannot_connect(hass: HomeAssistant, config_entry) -> None:
    """Test the reconfigure step reports an error when unreachable."""
    with patch(
        "custom_components.somneo.config_flow.Somneo"
    ) as somneo_cls:
        somneo_cls.return_value.get_device_info = AsyncMock(
            side_effect=Exception("boom")
        )
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_RECONFIGURE,
                "entry_id": config_entry.entry_id,
            },
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: HOST, CONF_NAME: NAME},
        )
        assert result["type"] == FlowResultType.FORM
        assert result["errors"] == {"base": "cannot_connect"}

async def test_form_flow_cannot_connect(hass: HomeAssistant) -> None:
    """Test the user step reports an error when the device is unreachable."""
    with patch(
        "custom_components.somneo.config_flow.Somneo"
    ) as somneo_cls:
        somneo_cls.return_value.get_device_info = AsyncMock(
            side_effect=Exception("boom")
        )
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: HOST, CONF_NAME: NAME},
        )
        assert result["type"] == FlowResultType.FORM
        assert result["errors"] == {"base": "cannot_connect"}
