"""Platform for select entity to catch alarm days."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.select import SelectEntity

from .const import DOMAIN, WORKDAYS, WEEKEND, TOMORROW, EVERYDAY, UNKNOWN, WORKDAYS_ICON
from .entity import SmartSleepEntity


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add SmartSleep from config_entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    unique_id = config_entry.unique_id
    assert unique_id is not None
    name = config_entry.data[CONF_NAME]
    device_info = config_entry.data["dev_info"]

    alarms = []
    # Add hour & min number_entity for each alarms
    for alarm in list(coordinator.data["alarms"]):
        alarms.append(SmartSleepDays(coordinator, unique_id, name, device_info, alarm))

    async_add_entities(alarms, update_before_add=True)


class SmartSleepDays(SmartSleepEntity, SelectEntity):
    _attr_should_poll = True
    _attr_icon = WORKDAYS_ICON
    _attr_assumed_state = False
    _attr_available = True
    _attr_options = [WORKDAYS, WEEKEND, TOMORROW, EVERYDAY, UNKNOWN]
    _attr_current_option = WORKDAYS

    def __init__(self, coordinator, unique_id, name, dev_info, alarm):
        """Initialize number entities."""
        super().__init__(coordinator, unique_id, name, dev_info, alarm)

        self._attr_translation_key = alarm + "_days"
        self._alarm = alarm

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_current_option = self.coordinator.data["alarms_day"][self._alarm]
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Called when user adjust the option in the UI."""
        await self.coordinator.async_set_alarm_day(self._alarm, option)
