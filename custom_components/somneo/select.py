"""Select entities for Somneo."""
import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pysomneo import LIGHT_CURVES, SOUND_DUSK

from .const import (
    CUSTOM,
    DOMAIN,
    EVERYDAY,
    SUNSET_ICON,
    TOMORROW,
    WEEKEND,
    WORKDAYS,
    WORKDAYS_ICON,
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
    """Representation of a alarm days."""

    _attr_should_poll = True
    _attr_icon = WORKDAYS_ICON
    _attr_assumed_state = False
    _attr_available = True
    _attr_options = [WORKDAYS, WEEKEND, TOMORROW, EVERYDAY, CUSTOM]
    _attr_current_option = WORKDAYS

    def __init__(self, coordinator, unique_id, name, dev_info, alarm):
        """Initialize number entities."""
        super().__init__(coordinator, unique_id, name, dev_info, "alarm" + str(alarm))

        self._attr_translation_key = "alarm" + str(alarm) + "_days"
        self._alarm = alarm

    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.debug(self.coordinator.data["alarms"][self._alarm]["days_type"])
        self._attr_current_option = self.coordinator.data["alarms"][self._alarm][
            "days_type"
        ]
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Adjust the option in the UI."""
        await self.coordinator.async_set_alarm(self._alarm, days=option)


class SomneoSunsetSound(SomneoEntity, SelectEntity):
    """Representation of a sunset sound source."""

    _attr_should_poll = True
    _attr_icon = SUNSET_ICON
    _attr_translation_key = "sunset_sound"
    _attr_assumed_state = False
    _attr_available = True
    _attr_options = [item.replace(" ", "_") for item in SOUND_DUSK.keys()]
    _attr_current_option = "soft_rain"

    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.debug(self.coordinator.data["sunset"]["sound"])
        self._attr_current_option = self.coordinator.data["sunset"]["sound"].replace(
            " ", "_"
        )
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Adjust the option in the UI."""
        await self.coordinator.async_set_sunset(sound=option.replace("_", " "))


class SomneoSunsetCurve(SomneoEntity, SelectEntity):
    """Representation of a sunset curve."""

    _attr_should_poll = True
    _attr_icon = SUNSET_ICON
    _attr_translation_key = "sunset_curve"
    _attr_assumed_state = False
    _attr_available = True
    _attr_current_option = "sunny_day"

    @property
    def options(self) -> list:
        """Return a set of selectable options."""
        return [item.replace(" ", "_") for item in LIGHT_CURVES[self.coordinator.somneo.version]]

    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.debug(self.coordinator.data["sunset"]["curve"])
        self._attr_current_option = self.coordinator.data["sunset"]["curve"].replace(
            " ", "_"
        )
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Adjust the option in the UI."""
        await self.coordinator.async_set_sunset(curve=option.replace("_", " "))
