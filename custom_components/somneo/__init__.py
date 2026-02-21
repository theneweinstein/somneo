"""Support for Philips Somneo devices."""

from __future__ import annotations

import asyncio
import functools as ft
from datetime import time, timedelta
import logging

import requests
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pysomneo import Somneo

from .const import CONF_SESSION, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.BUTTON,
    Platform.LIGHT,
    Platform.MEDIA_PLAYER,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TEXT,
    Platform.TIME,
]
SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Somneo component."""
    host = entry.data[CONF_HOST]
    use_session = entry.options.get(CONF_SESSION, True)

    coordinator = SomneoCoordinator(hass, host, use_session=use_session)
    entry.async_on_unload(entry.add_update_listener(update_listener))

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_entry(hass, config_entry: ConfigEntry):
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:
        new = {**config_entry.data}
        new.update({"options": {"use_session": True}})

        config_entry.version = 3
        hass.config_entries.async_update_entry(config_entry, data=new)

    if config_entry.version == 2:
        new = {**config_entry.data}
        use_session = new.pop("use_session")
        new.update({"options": {"use_session": use_session}})

        config_entry.version = 3
        hass.config_entries.async_update_entry(config_entry, data=new)

    if config_entry.version == 3:
        new = {**config_entry.data}
        options = {CONF_SESSION: True}
        config_entry.version = 4
        hass.config_entries.async_update_entry(config_entry, data=new, options=options)

    _LOGGER.info("Migration to version %s successful", config_entry.version)

    return True


class SomneoCoordinator(DataUpdateCoordinator):
    """Representation of a Somneo Coordinator."""

    def __init__(
        self, hass: HomeAssistant, host: str, use_session: bool = True
    ) -> None:
        """Initialize Somneo client."""
        self.somneo = Somneo(host, use_session=use_session)
        self.state_lock = asyncio.Lock()

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
            update_method=self._async_update,
            request_refresh_debouncer=Debouncer(
                hass, _LOGGER, cooldown=1.0, immediate=False
            ),
        )

    async def _async_update(self):
        """Fetch the latest data."""
        if self.state_lock.locked():
            return self.data

        try:
            # HGet new data from the library
            return await self.hass.async_add_executor_job(self.somneo.fetch_data)
        except (requests.exceptions.RequestException, Exception) as err:
            # Log e without crashing. Return old data to avoid entities become 'None'.
            _LOGGER.warning(
                "Somneo verbinding mislukt (is het apparaat offline?): %s", err
            )
            if self.data is None:
                return {}  # Avoid NoneType errors at the first start.
            return self.data

    async def async_toggle_light(
        self, state: bool, brightness: int | None = None
    ) -> None:
        """Toggle the main light."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(
                ft.partial(self.somneo.toggle_light, state, brightness=brightness)
            )
            await self.async_request_refresh()

    async def async_toggle_nightlight(self, state: bool) -> None:
        """Toggle the night light."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(
                self.somneo.toggle_night_light, state
            )
            await self.async_request_refresh()

    async def async_toggle_alarm(self, alarm: str, state: bool) -> None:
        """Toggle an alarm."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(
                self.somneo.toggle_alarm, alarm, state
            )
            await self.async_request_refresh()

    async def async_dismiss_alarm(self) -> None:
        """Dismiss alarm."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.somneo.dismiss_alarm)
            await self.async_request_refresh()

    async def async_set_alarm(
        self, alarm: str, alarm_time: time | None = None, days: str | list | None = None
    ):
        """Set alarm time."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(
                ft.partial(self.somneo.set_alarm, alarm, v_time=alarm_time, days=days)
            )
            await self.async_request_refresh()

    async def async_toggle_alarm_powerwake(self, alarm: str, state: bool):
        """Toggle powerwake (default 10 minutes)."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(
                ft.partial(
                    self.somneo.set_alarm_powerwake, alarm, onoff=state, delta=10
                )
            )
            await self.async_request_refresh()

    async def async_set_alarm_powerwake(self, alarm: str, delta: int = 0):
        """Set powerwake time."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(
                ft.partial(
                    self.somneo.set_alarm_powerwake,
                    alarm,
                    onoff=bool(delta),
                    delta=delta,
                )
            )
            await self.async_request_refresh()

    async def async_snooze_alarm(self) -> None:
        """Snooze alarm."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.somneo.snooze_alarm)
            await self.async_request_refresh()

    async def async_set_snooze_time(self, snooze_time):
        """Set snooze time."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(
                self.somneo.set_snooze_time, int(snooze_time)
            )
            await self.async_request_refresh()

    async def async_set_alarm_light(
        self, alarm: str, curve: str = "sunny day", level: int = 20, duration: int = 30
    ):
        """Adjust the light settings of an alarm."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(
                ft.partial(
                    self.somneo.set_alarm_light,
                    alarm,
                    curve=curve,
                    level=level,
                    duration=duration,
                )
            )
            await self.async_request_refresh()

    async def async_set_alarm_sound(
        self, alarm: str, source="wake-up", level=12, channel="forest birds"
    ):
        """Adjust the sound settings of an alarm."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(
                ft.partial(
                    self.somneo.set_alarm_sound,
                    alarm,
                    source=source,
                    level=level,
                    channel=channel,
                )
            )
            await self.async_request_refresh()

    async def async_remove_alarm(self, alarm: str):
        """Remove alarm from list in Somneo app."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.somneo.remove_alarm, alarm)

    async def async_add_alarm(self, alarm: str):
        """Add alarm to list in Somneo app."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.somneo.add_alarm, alarm)

    async def async_player_toggle(self, state: bool):
        """Toggle the audio player."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.somneo.toggle_player, state)
            await self.async_request_refresh()

    async def async_set_player_volume(self, volume: float):
        """Set the volume of the audio player."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(
                self.somneo.set_player_volume, volume
            )
            await self.async_request_refresh()

    async def async_set_player_source(self, source: str):
        """Set the volume of the audio player."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(
                self.somneo.set_player_source, source
            )
            await self.async_request_refresh()

    async def async_toggle_sunset(self, state: bool) -> None:
        """Toggle the main light."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(self.somneo.toggle_sunset, state)
            await self.async_request_refresh()

    async def async_set_sunset(
        self,
        curve: str | None = None,
        level: int | None = None,
        duration: int | None = None,
        sound: str | None = None,
        volume: int | None = None,
    ):
        """Adjust the sunset settings."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(
                ft.partial(
                    self.somneo.set_sunset,
                    curve=curve,
                    level=level,
                    duration=duration,
                    sound=sound,
                    volume=volume,
                )
            )
            await self.async_request_refresh()

    async def async_set_display(
        self, state: bool | None = None, brightness: int | None = None
    ):
        """Adjust the display."""
        async with self.state_lock:
            await self.hass.async_add_executor_job(
                ft.partial(self.somneo.set_display, state=state, brightness=brightness)
            )
            await self.async_request_refresh()
