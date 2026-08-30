"""Constants for the Somneo integration."""
from typing import Final

from homeassistant.const import (
    LIGHT_LUX,
    PERCENTAGE,
    UnitOfSoundPressure,
    UnitOfTemperature,
)

DOMAIN: Final = "somneo"

DEFAULT_NAME: Final = "Somneo"

WORKDAYS: Final = "workdays"
WEEKEND: Final = "weekend"
TOMORROW: Final = "tomorrow"
EVERYDAY: Final = "daily"
CUSTOM: Final = "custom"

ATTR_CURVE: Final = "curve"
ATTR_LEVEL: Final = "level"
ATTR_DURATION: Final = "duration"
ATTR_SOURCE: Final = "source"
ATTR_CHANNEL: Final = "channel"

SENSORS: Final = {
    "temperature": UnitOfTemperature.CELSIUS,
    "humidity": PERCENTAGE,
    "luminance": LIGHT_LUX,
    "noise": UnitOfSoundPressure.DECIBEL,
}

