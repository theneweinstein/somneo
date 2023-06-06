"""A entity class for SmartSleep integration."""
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SmartSleepCoordinator
from .const import DOMAIN


class SmartSleepEntity(CoordinatorEntity[SmartSleepCoordinator]):
    """SmartSleep entity class."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SmartSleepCoordinator,
        unique_id: str,
        name: str,
        dev_info: dict,
        identifier: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)

        self._attr_unique_id = unique_id + "_" + identifier
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            manufacturer=dev_info["manufacturer"],
            model=f"{dev_info['model']} {dev_info['modelnumber']}",
            name=name,
        )
        self._attr_has_entity_name = True
