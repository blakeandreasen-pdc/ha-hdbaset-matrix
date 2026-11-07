"""Selects: input routing per output, EDID per input."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import EDID_OPTIONS
from .entity import MatrixEntity

_EDID_BY_LABEL = {v: k for k, v in EDID_OPTIONS.items()}


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddEntitiesCallback) -> None:
    rt = entry.runtime_data
    ents: list[SelectEntity] = [
        OutputSourceSelect(rt.coordinator, o, name) for o, name in enumerate(rt.outputs, start=1)
    ]
    ents += [InputEdidSelect(rt.coordinator, i, name) for i, name in enumerate(rt.inputs, start=1)]
    async_add_entities(ents)


class OutputSourceSelect(MatrixEntity, SelectEntity):
    _attr_icon = "mdi:video-input-hdmi"

    def __init__(self, coordinator, output: int, name: str) -> None:
        super().__init__(coordinator, f"output_{output}_source", f"{name} source")
        self._output = output

    @property
    def options(self) -> list[str]:
        return self.runtime.inputs

    @property
    def current_option(self) -> str | None:
        i = self.coordinator.data.route.get(self._output)
        return self.runtime.inputs[i - 1] if i else None

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_command(
            self.coordinator.client.set_route(self._output, self.runtime.inputs.index(option) + 1)
        )


class InputEdidSelect(MatrixEntity, SelectEntity):
    _attr_icon = "mdi:monitor-screenshot"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_options = list(EDID_OPTIONS.values())

    def __init__(self, coordinator, input_: int, name: str) -> None:
        super().__init__(coordinator, f"input_{input_}_edid", f"{name} EDID")
        self._input = input_

    @property
    def current_option(self) -> str | None:
        code = self.coordinator.data.edid.get(self._input)
        return EDID_OPTIONS.get(code, code) if code else None

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_command(
            self.coordinator.client.set_edid(self._input, _EDID_BY_LABEL[option])
        )
