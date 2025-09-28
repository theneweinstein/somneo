"""Select entities for Somneo."""
import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pysomneo import FM_PRESETS

from .const import (
    CUSTOM,
    DOMAIN,
    EVERYDAY,
    TOMORROW,
    WEEKEND,
    WORKDAYS,
)
from .entity import SomneoEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add Somneo from config_entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    unique_id = config_entry.unique_id
    assert unique_id is not None
    name = config_entry.data[CONF_NAME]
    device_info = config_entry.data["dev_info"]

    alarms = []
    # Add hour & min number_entity for each alarms
    for alarm in list(coordinator.data["alarms"]):
        alarms.append(SomneoDays(coordinator, unique_id, name, device_info, alarm))

    sunset = [
        SomneoSunsetSound(coordinator, unique_id, name, device_info, "sunset_sound"),
        SomneoSunsetCurve(coordinator, unique_id, name, device_info, "sunset_curve"),
    ]

    async_add_entities(alarms, update_before_add=True)
    async_add_entities(sunset, update_before_add=True)


class SomneoDays(SomneoEntity, SelectEntity):
    """Representation of alarm days."""

    _attr_should_poll = True
    _attr_assumed_state = False
    _attr_available = True
    _attr_options = [WORKDAYS, WEEKEND, TOMORROW, EVERYDAY, CUSTOM]
    _attr_current_option = WORKDAYS
    _attr_translation_key = "days"

    def __init__(self, coordinator, unique_id, name, dev_info, alarm):
        """Initialize select entity for alarm days."""
        super().__init__(coordinator, unique_id, name, dev_info, "alarm" + str(alarm))
        self._attr_translation_placeholders = {"number": str(alarm)}
        self._alarm = alarm

    @callback
    def _handle_coordinator_update(self) -> None:
        new_option = self.coordinator.data["alarms"][self._alarm]["days_type"]
        if new_option != self._attr_current_option:
            _LOGGER.debug(
                "Alarm %s days changed: %s -> %s",
                self._alarm,
                self._attr_current_option,
                new_option,
            )
            self._attr_current_option = new_option
            self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Adjust the option in the UI."""
        await self.coordinator.async_set_alarm(self._alarm, days=option)


class SomneoSunsetSound(SomneoEntity, SelectEntity):
    """Representation of a sunset sound source."""

    _attr_should_poll = True
    _attr_translation_key = "sunset_sound"
    _attr_assumed_state = False
    _attr_available = True
    _attr_current_option = "soft_rain"

    @property
    def options(self) -> list:
        """Return a set of selectable options."""
        return [
            item.replace(" ", "_") for item in self.coordinator.somneo.dusk_sound_themes
        ] + [item.replace(" ", "_") for item in FM_PRESETS]

    @callback
    def _handle_coordinator_update(self) -> None:
        new_option = self.coordinator.data["sunset"]["sound"].replace(" ", "_")
        if new_option != self._attr_current_option:
            _LOGGER.debug(
                "Sunset sound changed: %s -> %s",
                self._attr_current_option,
                new_option,
            )
            self._attr_current_option = new_option
            self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Adjust the option in the UI."""
        await self.coordinator.async_set_sunset(sound=option.replace("_", " "))


class SomneoSunsetCurve(SomneoEntity, SelectEntity):
    """Representation of a sunset curve."""

    _attr_should_poll = True
    _attr_translation_key = "sunset_curve"
    _attr_assumed_state = False
    _attr_available = True
    _attr_current_option = "sunny_day"

    @property
    def options(self) -> list:
        """Return a set of selectable options."""
        return [item.replace(" ", "_") for item in self.coordinator.somneo.dusk_light_themes]

    @callback
    def _handle_coordinator_update(self) -> None:
        new_option = self.coordinator.data["sunset"]["curve"].replace(" ", "_")
        if new_option != self._attr_current_option:
            _LOGGER.debug(
                "Sunset curve changed: %s -> %s",
                self._attr_current_option,
                new_option,
            )
            self._attr_current_option = new_option
            self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Adjust the option in the UI."""
        await self.coordinator.async_set_sunset(curve=option.replace("_", " "))
