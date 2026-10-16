"""An entity class for the Somneo integration."""
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SomneoCoordinator


class SomneoEntity(CoordinatorEntity[SomneoCoordinator]):
    """Somneo entity base class."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SomneoCoordinator,
        unique_id: str,
        identifier: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)

        self._attr_unique_id = f"{unique_id}_{identifier}"
        self._attr_device_info = coordinator.device_info

