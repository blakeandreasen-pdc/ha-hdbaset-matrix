"""HDBaseT 4x4 HDMI matrix integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MatrixClient
from .const import CONF_INPUTS, CONF_OUTPUTS, DEFAULT_INPUTS, DEFAULT_OUTPUTS
from .coordinator import MatrixCoordinator

PLATFORMS = [Platform.MEDIA_PLAYER, Platform.SELECT, Platform.SWITCH]


@dataclass
class MatrixRuntime:
    coordinator: MatrixCoordinator
    inputs: list[str]
    outputs: list[str]


type MatrixConfigEntry = ConfigEntry[MatrixRuntime]


async def async_setup_entry(hass: HomeAssistant, entry: MatrixConfigEntry) -> bool:
    client = MatrixClient(async_get_clientsession(hass), entry.data[CONF_HOST])
    coordinator = MatrixCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = MatrixRuntime(
        coordinator=coordinator,
        inputs=list(entry.options.get(CONF_INPUTS, DEFAULT_INPUTS)),
        outputs=list(entry.options.get(CONF_OUTPUTS, DEFAULT_OUTPUTS)),
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    return True


async def _async_reload(hass: HomeAssistant, entry: MatrixConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: MatrixConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
