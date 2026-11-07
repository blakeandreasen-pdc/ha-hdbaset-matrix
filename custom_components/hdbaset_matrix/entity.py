"""Base entity for the HDBaseT Matrix."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MatrixCoordinator


class MatrixEntity(CoordinatorEntity[MatrixCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: MatrixCoordinator, key: str, name: str | None) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.unique_id}_{key}"
        self._attr_name = name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id)},
            name=entry.title,
            manufacturer="HDBaseT",
            model="4x4 HDMI Matrix",
            configuration_url=f"http://{entry.data['host']}/",
        )

    @property
    def runtime(self):
        return self.coordinator.config_entry.runtime_data
