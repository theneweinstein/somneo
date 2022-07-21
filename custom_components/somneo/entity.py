"""A entity class for Somneo integration."""
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SomneoCoordinator
from .const import DOMAIN


class SomneoEntity(CoordinatorEntity[SomneoCoordinator]):
    """Somneo entity class."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SomneoCoordinator,
        unique_id: str,
        name: str,
        dev_info: dict,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)

        self._attr_unique_id = unique_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            manufacturer=dev_info['manufacturer'],
            model=f"{dev_info['model']} {dev_info['modelnumber']}",
            name=name,
        )