"""Config flow for Nevermind."""
from __future__ import annotations

import hashlib
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_API_KEY, CONF_HOST
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NevermindApiClient, NevermindAuthError, NevermindConnectionError
from .const import DOMAIN

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_API_KEY): str,
    }
)


class NevermindConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            client = NevermindApiClient(
                async_get_clientsession(self.hass), user_input[CONF_HOST], user_input[CONF_API_KEY]
            )
            try:
                await client.async_list_ideas()
            except NevermindAuthError:
                errors["base"] = "invalid_auth"
            except NevermindConnectionError:
                errors["base"] = "cannot_connect"
            else:
                # No account/whoami endpoint exists to key off — the API key
                # itself is a 1:1 stand-in for the Nevermind account.
                await self.async_set_unique_id(
                    hashlib.sha256(user_input[CONF_API_KEY].encode()).hexdigest()
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=user_input[CONF_HOST], data=user_input)

        return self.async_show_form(step_id="user", data_schema=STEP_USER_SCHEMA, errors=errors)
