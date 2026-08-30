"""Support for Philips Somneo devices."""
from __future__ import annotations

import logging
from datetime import datetime, time, timedelta
from typing import cast

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as ha_dt
from pysomneo import Somneo

from .const import DEFAULT_NAME, DOMAIN
from .models import SomneoData

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
SCAN_INTERVAL = timedelta(seconds=10)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Somneo component."""
    host = entry.data[CONF_HOST]
    name = entry.data.get(CONF_NAME, DEFAULT_NAME)
    dev_info = entry.data.get("dev_info")

    coordinator = SomneoCoordinator(hass, host, name, dev_info)
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


async def async_migrate_entry(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> bool:
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

    _LOGGER.info("Migration to version %s successful", config_entry.version)

    return True


class SomneoCoordinator(DataUpdateCoordinator[SomneoData]):
    """Representation of a Somneo Coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        name: str,
        dev_info: dict[str, str] | None = None,
    ) -> None:
        """Initialize Somneo client."""
        self.somneo = Somneo(host)

        # Build a stable DeviceInfo for all entities of this device.
        dev_info = dev_info or {}
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, dev_info.get("serial", host))},
            manufacturer=dev_info.get("manufacturer", "Royal Philips Electronics"),
            model=" ".join(
                part
                for part in (
                    dev_info.get("model", "Wake-up Light"),
                    dev_info.get("modelnumber"),
                )
                if part
            ),
            name=name,
        )

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

    async def _async_update(self) -> SomneoData:
        """Fetch the latest data."""
        try:
            data = cast(SomneoData, await self.somneo.fetch_data())

            if data is None:
                _LOGGER.debug("Somneo fetch returned None, using previous data")
                return self.data or self._default_data()

            # Convert naive next_alarm datetime to timezone-aware UTC datetime
            # using the Home Assistant configured timezone
            next_alarm = data.get("next_alarm")
            if isinstance(next_alarm, datetime) and next_alarm.tzinfo is None:
                ha_tz = ha_dt.get_time_zone(self.hass.config.time_zone)
                if ha_tz:
                    data["next_alarm"] = next_alarm.replace(tzinfo=ha_tz).astimezone(
                        ha_dt.UTC
                    )

            return data

        except Exception as e:  # noqa: BLE001
            _LOGGER.error("Error fetching data from Somneo: %s", e)
            # If we have previous data, return it; otherwise return empty dict with defaults
            if self.data is not None:
                return self.data
            return self._default_data()

    def _default_data(self) -> SomneoData:
        """Return a data dictionary with default values to prevent KeyError in platforms."""
        return {
            "alarms": {},
            "player": {},
            "sunset": {},
            "next_alarm": None,
            "snooze_time": 5,
            "temperature": None,
            "humidity": None,
            "luminance": None,
            "noise": None,
            "light_is_on": False,
            "light_brightness": 0,
            "nightlight_is_on": False,
            "somneo_status": "unknown",
            "display_always_on": False,
            "display_brightness": 0,
        }

    async def async_toggle_light(
        self, state: bool, brightness: int | None = None
    ) -> None:
        """Toggle the main light."""
        await self.somneo.toggle_light(state, brightness=brightness)
        await self.async_request_refresh()

    async def async_toggle_nightlight(self, state: bool) -> None:
        """Toggle the night light."""
        await self.somneo.toggle_night_light(state)
        await self.async_request_refresh()

    async def async_toggle_alarm(self, alarm: str, state: bool) -> None:
        """Toggle an alarm."""
        await self.somneo.toggle_alarm(alarm, state)
        await self.async_request_refresh()

    async def async_dismiss_alarm(self) -> None:
        """Dismiss alarm."""
        await self.somneo.dismiss_alarm()
        await self.async_request_refresh()

    async def async_set_alarm(
        self, alarm: str, alarm_time: time | None = None, days: str | list | None = None
    ) -> None:
        """Set alarm time."""
        await self.somneo.set_alarm(alarm, v_time=alarm_time, days=days)
        await self.async_request_refresh()

    async def async_toggle_alarm_powerwake(self, alarm: str, state: bool) -> None:
        """Toggle powerwake (default 10 minutes)."""
        await self.somneo.set_alarm_powerwake(alarm, onoff=state, delta=10)
        await self.async_request_refresh()

    async def async_set_alarm_powerwake(self, alarm: str, delta: int = 0) -> None:
        """Set powerwake time."""
        await self.somneo.set_alarm_powerwake(
            alarm, onoff=bool(delta), delta=delta
        )
        await self.async_request_refresh()

    async def async_snooze_alarm(self) -> None:
        """Snooze alarm."""
        await self.somneo.snooze_alarm()
        await self.async_request_refresh()

    async def async_set_snooze_time(self, snooze_time: int | str) -> None:
        """Set snooze time."""
        await self.somneo.set_snooze_time(int(snooze_time))
        await self.async_request_refresh()

    async def async_set_alarm_light(
        self, alarm: str, curve: str = "sunny day", level: int = 20, duration: int = 30
    ) -> None:
        """Adjust the light settings of an alarm."""
        await self.somneo.set_alarm_light(
            alarm, curve=curve, level=level, duration=duration
        )
        await self.async_request_refresh()

    async def async_set_alarm_sound(
        self, alarm: str, source: str = "wake-up", level: int = 12, channel: str = "forest birds"
    ) -> None:
        """Adjust the sound settings of an alarm."""
        await self.somneo.set_alarm_sound(
            alarm, source=source, level=level, channel=channel
        )
        await self.async_request_refresh()

    async def async_remove_alarm(self, alarm: str) -> None:
        """Remove alarm from list in Somneo app."""
        await self.somneo.remove_alarm(alarm)

    async def async_add_alarm(self, alarm: str) -> None:
        """Add alarm to list in Somneo app."""
        await self.somneo.add_alarm(alarm)

    async def async_player_toggle(self, state: bool) -> None:
        """Toggle the audio player."""
        await self.somneo.toggle_player(state)
        await self.async_request_refresh()

    async def async_set_player_volume(self, volume: float) -> None:
        """Set the volume of the audio player."""
        await self.somneo.set_player_volume(volume)
        await self.async_request_refresh()

    async def async_set_player_source(self, source: str) -> None:
        """Set the source of the audio player."""
        await self.somneo.set_player_source(source)
        await self.async_request_refresh()

    async def async_toggle_sunset(self, state: bool) -> None:
        """Toggle the main light."""
        await self.somneo.toggle_sunset(state)
        await self.async_request_refresh()

    async def async_set_sunset(
        self,
        curve: str | None = None,
        level: int | None = None,
        duration: int | None = None,
        sound: str | None = None,
        volume: int | None = None,
    ) -> None:
        """Adjust the sunset settings."""
        await self.somneo.set_sunset(
            curve=curve, level=level, duration=duration, sound=sound, volume=volume
        )
        await self.async_request_refresh()

    async def async_set_display(
        self, state: bool | None = None, brightness: int | None = None
    ) -> None:
        """Adjust the display."""
        await self.somneo.set_display(state=state, brightness=brightness)
        await self.async_request_refresh()
