"""Fixtures for the Somneo integration tests."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.somneo.const import DOMAIN

from .common import FAKE_DATA, FAKE_DEVICE_INFO, HOST, NAME, SERIAL


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations) -> None:
    """Enable loading the custom component from the repository."""

# Every async method of the Somneo client that the integration may call.
SOMNEO_METHODS = (
    "fetch_data",
    "get_device_info",
    "toggle_light",
    "toggle_night_light",
    "toggle_alarm",
    "set_alarm",
    "set_alarm_powerwake",
    "snooze_alarm",
    "dismiss_alarm",
    "set_snooze_time",
    "set_alarm_light",
    "set_alarm_sound",
    "remove_alarm",
    "add_alarm",
    "toggle_player",
    "set_player_volume",
    "set_player_source",
    "toggle_sunset",
    "set_sunset",
    "set_display",
)


@pytest.fixture
def mock_somneo():
    """
    Mock the Somneo client used by the integration.

    Patches both the coordinator's and the config flow's reference to
    ``pysomneo.Somneo`` so no real network I/O happens during tests.
    """
    with (
        patch("custom_components.somneo.Somneo") as somneo_cls,
        patch("custom_components.somneo.config_flow.Somneo") as somneo_cf_cls,
    ):
        instance = somneo_cls.return_value
        for method in SOMNEO_METHODS:
            setattr(instance, method, AsyncMock())
        instance.fetch_data.return_value = dict(FAKE_DATA)
        instance.get_device_info.return_value = dict(FAKE_DEVICE_INFO)

        # The config flow creates its own Somneo instance; make it return the
        # same device info.
        somneo_cf_cls.return_value.get_device_info.return_value = dict(
            FAKE_DEVICE_INFO
        )

        yield instance


@pytest.fixture
def config_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Create a mock config entry and add it to hass."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=NAME,
        unique_id=SERIAL,
        data={CONF_HOST: HOST, CONF_NAME: NAME},
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
async def setup_integration(
    hass: HomeAssistant, config_entry, mock_somneo
) -> MockConfigEntry:
    """Set up the full Somneo integration with a mocked device."""
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    # Push the already-fetched coordinator data to all just-subscribed
    # entities so their state is deterministic without waiting for the
    # 10 second polling interval.
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    return config_entry
