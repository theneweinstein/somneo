"""Platform for select entity to catch alarm days."""
import logging

from homeassistant.components.select import SelectEntity

from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """ Add Somneo from config_entry."""
    name = config_entry.data[CONF_NAME]
    data = hass.data[DOMAIN]
    dev_info = data.dev_info

    device_info = {
        "identifiers": {(DOMAIN, dev_info['serial'])},
        "name": 'Somneo',
        "manufacturer": dev_info['manufacturer'],
        "model": f"{dev_info['model']} {dev_info['modelnumber']}",
    }

    alarms = []
    # Add hour & min number_entity for each alarms
    for alarm in list(data.somneo.alarms()):
        alarms.append(SomneoDays(name, data, device_info, dev_info['serial'], alarm))

    async_add_entities(alarms, True)

class SomneoDays(SelectEntity):
    _attr_should_poll = True
    _attr_icon = WORKDAYS_ICON
    _attr_assumed_state = False
    _attr_available = True

    def __init__(self, name, data, device_info, serial, alarm):
        """Initialize number entities."""
        self._data = data
        self._attr_name = name + "_" + alarm + "_days"
        self._alarm = alarm
        self._attr_unique_id = serial + '_' + alarm + '_days'
        self._alarm_date = None
        self._attr_device_info = device_info
        self._attr_options = [WORKDAYS, WEEKEND, TOMORROW, EVERYDAY, UNKNOWN]
        self._attr_current_option = WORKDAYS

    def select_option(self, option: str) -> None:
        """Called when user adjust the option in the UI."""
        _LOGGER.debug(option)
        
        self._attr_current_option = option

        if option == WORKDAYS:
            self._data.somneo.set_workdays_alarm(self._alarm)
            _LOGGER.debug('Optie is werkday')
        elif option == WEEKEND:
            self._data.somneo.set_weekend_alarm(self._alarm)
            _LOGGER.debug('Optie is weekend')
        elif option == TOMORROW:
            self._data.somneo.set_tomorrow_alarm(self._alarm)
            _LOGGER.debug('Optie is morgen')
        elif option == EVERYDAY:
            self._data.somneo.set_everyday_alarm(self._alarm)
            _LOGGER.debug('Optie is elke dag')

    async def async_update(self):
        """Get the latest data and updates the states."""
        await self._data.update()

        if self._data.somneo.is_everyday(self._alarm):
            self._attr_current_option = EVERYDAY
        elif self._data.somneo.is_workday(self._alarm):
            self._attr_current_option = WORKDAYS
        elif self._data.somneo.is_weekend(self._alarm):
            self._attr_current_option = WEEKEND
        elif self._data.somneo.is_tomorrow(self._alarm):
            self._attr_current_option = TOMORROW
        else:
            self._attr_current_option = UNKNOWN