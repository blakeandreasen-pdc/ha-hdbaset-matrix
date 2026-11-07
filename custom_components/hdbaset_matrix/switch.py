"""Switches: power and audio per output."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import MatrixEntity


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback) -> None:
    rt = entry.runtime_data
    ents: list[SwitchEntity] = []
    for o, name in enumerate(rt.outputs, start=1):
        ents.append(OutputPowerSwitch(rt.coordinator, o, name))
        ents.append(OutputAudioSwitch(rt.coordinator, o, name))
    async_add_entities(ents)


class OutputPowerSwitch(MatrixEntity, SwitchEntity):
    _attr_icon = "mdi:power"

    def __init__(self, coordinator, output: int, name: str) -> None:
        super().__init__(coordinator, f"output_{output}_power", f"{name} power")
        self._output = output

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.power.get(self._output)

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_command(self.coordinator.client.set_power(self._output, True))

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_command(self.coordinator.client.set_power(self._output, False))


class OutputAudioSwitch(MatrixEntity, SwitchEntity):
    _attr_icon = "mdi:speaker"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator, output: int, name: str) -> None:
        super().__init__(coordinator, f"output_{output}_audio", f"{name} audio")
        self._output = output

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.audio.get(self._output)

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_command(self.coordinator.client.set_audio(self._output, True))

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_command(self.coordinator.client.set_audio(self._output, False))
