"""Button entities for Somneo."""
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DISMISS_ICON, DOMAIN, SNOOZE_ICON
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

    buttons = [
        SomneoDismiss(coordinator, unique_id, name, device_info, "alarm_dismiss"),
        SomneoSnooze(coordinator, unique_id, name, device_info, "alarm_snooze"),
    ]

    async_add_entities(buttons, update_before_add=True)


class SomneoDismiss(SomneoEntity, ButtonEntity):
    """Dismiss alarm button."""

    _attr_icon = DISMISS_ICON
    _attr_should_poll = True
    _attr_translation_key = "alarm_dismiss"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_dismiss_alarm()


class SomneoSnooze(SomneoEntity, ButtonEntity):
    """Snooze alarm button."""

    _attr_icon = SNOOZE_ICON
    _attr_should_poll = True
    _attr_translation_key = "alarm_snooze"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_snooze_alarm()
