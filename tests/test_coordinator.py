"""Tests for the Somneo coordinator."""
from __future__ import annotations

from datetime import datetime

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from custom_components.somneo import SomneoCoordinator
from custom_components.somneo.const import DOMAIN

from .common import FAKE_DATA, FAKE_DEVICE_INFO, HOST, NAME, SERIAL


@pytest.fixture
async def coordinator(
    hass: HomeAssistant, mock_somneo
) -> SomneoCoordinator:
    """Create a coordinator with mocked device data."""
    return SomneoCoordinator(hass, HOST, NAME, SERIAL)


async def test_default_data_shape(coordinator: SomneoCoordinator) -> None:
    """Test the fallback data dict contains all expected keys."""
    data = coordinator._default_data()
    assert data["alarms"] == {}
    assert data["player"] == {}
    assert data["sunset"] == {}
    assert data["next_alarm"] is None
    assert data["temperature"] is None
    assert data["light_is_on"] is False
    assert data["somneo_status"] == "unknown"


async def test_async_update_uses_fetched_data(
    coordinator: SomneoCoordinator, mock_somneo
) -> None:
    """Test the update method returns the device data."""
    data = await coordinator._async_update()
    assert data["temperature"] == FAKE_DATA["temperature"]
    assert data["light_is_on"] is True
    assert data["alarms"][0]["enabled"] is True
    mock_somneo.fetch_data.assert_awaited_once()


async def test_async_update_converts_naive_next_alarm(
    coordinator: SomneoCoordinator, mock_somneo
) -> None:
    """Test a naive next_alarm is converted to timezone-aware UTC."""
    naive = datetime(2026, 9, 1, 7, 30)
    mock_somneo.fetch_data.return_value = {**FAKE_DATA, "next_alarm": naive}
    data = await coordinator._async_update()
    next_alarm = data["next_alarm"]
    assert isinstance(next_alarm, datetime)
    assert next_alarm.tzinfo is not None
    # The naive value is interpreted in the HA configured timezone and
    # converted to UTC.
    ha_tz = dt_util.get_time_zone(coordinator.hass.config.time_zone)
    assert ha_tz is not None
    assert next_alarm == naive.replace(tzinfo=ha_tz).astimezone(dt_util.UTC)


async def test_async_update_keeps_aware_next_alarm(
    coordinator: SomneoCoordinator, mock_somneo
) -> None:
    """Test an already timezone-aware next_alarm is left untouched."""
    aware = datetime(2026, 9, 1, 7, 30, tzinfo=dt_util.UTC)
    mock_somneo.fetch_data.return_value = {**FAKE_DATA, "next_alarm": aware}
    data = await coordinator._async_update()
    assert data["next_alarm"] == aware


async def test_async_update_falls_back_to_default_on_none(
    coordinator: SomneoCoordinator, mock_somneo
) -> None:
    """Test None data falls back to defaults when no previous data exists."""
    mock_somneo.fetch_data.return_value = None
    data = await coordinator._async_update()
    assert data["somneo_status"] == "unknown"


async def test_async_update_falls_back_to_previous_data_on_error(
    coordinator: SomneoCoordinator, mock_somneo
) -> None:
    """Test an exception keeps the previous data instead of raising."""
    mock_somneo.fetch_data.return_value = dict(FAKE_DATA)
    await coordinator.async_refresh()
    assert coordinator.data["temperature"] == FAKE_DATA["temperature"]

    mock_somneo.fetch_data.side_effect = TimeoutError("device offline")
    await coordinator.async_refresh()
    # _async_update swallows the error and returns the previous data.
    assert coordinator.data["temperature"] == FAKE_DATA["temperature"]


async def test_fetch_device_info_builds_deviceinfo(
    hass: HomeAssistant, coordinator: SomneoCoordinator, mock_somneo
) -> None:
    """Test device info is fetched and used to build the DeviceInfo."""
    await coordinator.async_fetch_device_info()
    assert coordinator.device_info["identifiers"] == {(DOMAIN, SERIAL)}
    assert coordinator.device_info["manufacturer"] == FAKE_DEVICE_INFO[
        "manufacturer"
    ]
    assert coordinator.device_info["name"] == NAME


async def test_fetch_device_info_falls_back_on_error(
    hass: HomeAssistant, coordinator: SomneoCoordinator, mock_somneo
) -> None:
    """Test a failed device info fetch keeps the default DeviceInfo."""
    mock_somneo.get_device_info.side_effect = TimeoutError("offline")
    await coordinator.async_fetch_device_info()
    assert coordinator.device_info["identifiers"] == {(DOMAIN, SERIAL)}
    assert coordinator.device_info["model"] == "Wake-up Light"
