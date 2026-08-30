"""Media player entities for Somneo."""
from __future__ import annotations

import logging

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SomneoEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add Somneo light from config_entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    unique_id = config_entry.unique_id
    assert unique_id is not None

    async_add_entities(
        [SomneoMediaPlayer(coordinator, unique_id, "player")],
        update_before_add=True,
    )


class SomneoMediaPlayer(SomneoEntity, MediaPlayerEntity):
    """Representation of an Somneo Media player."""

    _attr_supported_features = (
        MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.SELECT_SOURCE
    )
    _attr_device_class = MediaPlayerDeviceClass.SPEAKER
    _attr_translation_key = "player"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update media player state from coordinator data."""
        player_data = self.coordinator.data["player"]
        self._attr_state = (
            MediaPlayerState.ON
            if player_data["state"]
            else MediaPlayerState.OFF
        )
        self._attr_volume_level = player_data["volume"]
        self._attr_source = player_data["source"]
        self._attr_source_list = player_data["possible_sources"]
        self.async_write_ha_state()

    async def async_turn_on(self) -> None:
        """Turn the player on."""
        await self.coordinator.async_player_toggle(True)

    async def async_turn_off(self) -> None:
        """Turn the player off."""
        await self.coordinator.async_player_toggle(False)

    async def async_set_volume_level(self, volume: float) -> None:
        """Set the volume level."""
        await self.coordinator.async_set_player_volume(volume)

    async def async_select_source(self, source: str) -> None:
        """Select a source."""
        await self.coordinator.async_set_player_source(source)
