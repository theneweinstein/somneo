
from homeassistant.const import (TEMP_CELSIUS, PERCENTAGE)
from typing import Final

DOMAIN: Final = 'somneo'
VERSION: Final = "0.3"

DEFAULT_NAME: Final = "Somneo"

CONF_SENS: Final = 'sensors'

ALARMS: Final = 'alarms'
HOURS: Final = 'hours'
MINUTES: Final = 'minutes'
WORKDAYS: Final = 'workdays'
WEEKEND: Final = 'weekend'
TOMORROW: Final = 'tomorrow'
EVERYDAY: Final = 'daily'
UNKNOWN: Final = 'unknown'

ALARMS_ICON: Final = 'hass:alarm'
HOURS_ICON: Final = 'hass:counter'
MINUTES_ICON: Final = 'hass:counter'
WORKDAYS_ICON: Final = 'hass:calendar-range'
WEEKEND_ICON: Final = 'hass:calendar-range'

ATTR_ALARM: Final = 'alarm'
ATTR_CURVE: Final = 'curve'
ATTR_LEVEL: Final = 'level'
ATTR_DURATION: Final = 'duration'
ATTR_SOURCE: Final = 'source'
ATTR_CHANNEL: Final = 'channel'


SENSORS: Final = {'temperature': TEMP_CELSIUS, 'humidity': PERCENTAGE, 'luminance': 'lux', 'noise': 'db'}

NOTIFICATION_ID: Final = "somneosensor_notification"
NOTIFICATION_TITLE: Final = "SomneoSensor Setup"



