"""Polling coordinator for the HDBaseT Matrix."""
from __future__ import annotations

from collections.abc import Awaitable
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MatrixClient, MatrixError, MatrixState
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class MatrixCoordinator(DataUpdateCoordinator[MatrixState]):
    """Polls the matrix and applies command responses immediately."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: MatrixClient) -> None:
        interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=interval),
        )
        self.client = client

    async def _async_update_data(self) -> MatrixState:
        try:
            return await self.client.get_state()
        except MatrixError as err:
            raise UpdateFailed(str(err)) from err

    async def async_command(self, coro: Awaitable[str]) -> None:
        """Run a command; the matrix answers with fresh status, so apply it right away."""
        try:
            text = await coro
        except MatrixError as err:
            raise HomeAssistantError(str(err)) from err
        if self.data is not None:
            try:
                self.data.apply(text)
            except MatrixError:
                await self.async_request_refresh()
                return
            self.async_set_updated_data(self.data)
        else:
            await self.async_request_refresh()
