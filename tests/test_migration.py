"""Tests for config entry migration."""
from __future__ import annotations

from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.somneo import async_migrate_entry
from custom_components.somneo.const import DOMAIN

from .common import HOST, NAME, SERIAL


async def test_migrate_v1_to_v4(hass: HomeAssistant) -> None:
    """Test a v1 entry (legacy options blob) migrates all the way to v4."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=SERIAL,
        version=1,
        data={
            CONF_HOST: HOST,
            CONF_NAME: NAME,
            "options": {"use_session": True},
        },
    )
    entry.add_to_hass(hass)
    assert await async_migrate_entry(hass, entry)
    assert entry.version == 4
    assert "options" not in entry.data
    assert entry.data[CONF_HOST] == HOST


async def test_migrate_v2_to_v4(hass: HomeAssistant) -> None:
    """Test a v2 entry (use_session in data) migrates to v4."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=SERIAL,
        version=2,
        data={CONF_HOST: HOST, CONF_NAME: NAME, "use_session": False},
    )
    entry.add_to_hass(hass)
    assert await async_migrate_entry(hass, entry)
    assert entry.version == 4
    assert "use_session" not in entry.data


async def test_migrate_v3_to_v4(hass: HomeAssistant) -> None:
    """Test a v3 entry (dev_info in data) migrates to v4."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=SERIAL,
        version=3,
        data={
            CONF_HOST: HOST,
            CONF_NAME: NAME,
            "dev_info": {"manufacturer": "Philips", "serial": SERIAL},
        },
    )
    entry.add_to_hass(hass)
    assert await async_migrate_entry(hass, entry)
    assert entry.version == 4
    assert "dev_info" not in entry.data
    assert entry.data[CONF_HOST] == HOST


async def test_migrate_current_version_unchanged(hass: HomeAssistant) -> None:
    """Test a current v4 entry is left untouched."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=SERIAL,
        version=4,
        data={CONF_HOST: HOST, CONF_NAME: NAME},
    )
    entry.add_to_hass(hass)
    assert await async_migrate_entry(hass, entry)
    assert entry.version == 4
