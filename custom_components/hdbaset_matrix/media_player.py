"""One media_player per matrix output: power + source (input) selection."""
from __future__ import annotations

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import MatrixEntity


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback) -> None:
    rt = entry.runtime_data
    async_add_entities(
        MatrixOutputPlayer(rt.coordinator, o, name) for o, name in enumerate(rt.outputs, start=1)
    )


class MatrixOutputPlayer(MatrixEntity, MediaPlayerEntity):
    _attr_supported_features = (
        MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.SELECT_SOURCE
    )
    _attr_icon = "mdi:video-input-hdmi"

    def __init__(self, coordinator, output: int, name: str) -> None:
        super().__init__(coordinator, f"output_{output}", name)
        self._output = output

    @property
    def state(self) -> MediaPlayerState | None:
        on = self.coordinator.data.power.get(self._output)
        if on is None:
            return None
        return MediaPlayerState.ON if on else MediaPlayerState.OFF

    @property
    def source_list(self) -> list[str]:
        return self.runtime.inputs

    @property
    def source(self) -> str | None:
        i = self.coordinator.data.route.get(self._output)
        return self.runtime.inputs[i - 1] if i else None

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "output": self._output,
            "input": self.coordinator.data.route.get(self._output),
            "audio": self.coordinator.data.audio.get(self._output),
        }

    async def async_turn_on(self) -> None:
        await self.coordinator.async_command(self.coordinator.client.set_power(self._output, True))

    async def async_turn_off(self) -> None:
        await self.coordinator.async_command(self.coordinator.client.set_power(self._output, False))

    async def async_select_source(self, source: str) -> None:
        if source not in self.runtime.inputs:
            raise ServiceValidationError(f"Unknown source {source!r}; options: {self.runtime.inputs}")
        await self.coordinator.async_command(
            self.coordinator.client.set_route(self._output, self.runtime.inputs.index(source) + 1)
        )
