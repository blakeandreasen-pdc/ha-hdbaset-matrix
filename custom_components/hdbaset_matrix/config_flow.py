"""Config and options flow for the HDBaseT Matrix."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MatrixClient, MatrixError, validate_host
from .const import (
    CONF_INPUTS,
    CONF_OUTPUTS,
    CONF_SCAN_INTERVAL,
    DEFAULT_INPUTS,
    DEFAULT_NAME,
    DEFAULT_OUTPUTS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    NUM_PORTS,
)


class MatrixConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                host = validate_host(user_input[CONF_HOST])
                mac = await MatrixClient(async_get_clientsession(self.hass), host).get_mac()
            except ValueError:
                errors[CONF_HOST] = "invalid_host"
            except MatrixError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(mac)
                self._abort_if_unique_id_configured(updates={CONF_HOST: host})
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME) or DEFAULT_NAME, data={CONF_HOST: host}
                )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return MatrixOptionsFlow()


class MatrixOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        opts = self.config_entry.options
        inputs = opts.get(CONF_INPUTS, DEFAULT_INPUTS)
        outputs = opts.get(CONF_OUTPUTS, DEFAULT_OUTPUTS)
        if user_input is not None:
            return self.async_create_entry(
                data={
                    CONF_INPUTS: [user_input[f"input_{i}"].strip() or f"Input {i}" for i in range(1, NUM_PORTS + 1)],
                    CONF_OUTPUTS: [user_input[f"output_{i}"].strip() or f"Output {i}" for i in range(1, NUM_PORTS + 1)],
                    CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                }
            )
        schema: dict = {}
        for i in range(1, NUM_PORTS + 1):
            schema[vol.Required(f"input_{i}", default=inputs[i - 1])] = str
        for i in range(1, NUM_PORTS + 1):
            schema[vol.Required(f"output_{i}", default=outputs[i - 1])] = str
        schema[
            vol.Required(CONF_SCAN_INTERVAL, default=opts.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
        ] = vol.All(vol.Coerce(int), vol.Range(min=2, max=300))
        return self.async_show_form(step_id="init", data_schema=vol.Schema(schema))
