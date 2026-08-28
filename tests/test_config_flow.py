"""Tests for the Nevermind config flow."""
from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.nevermind.api import NevermindAuthError, NevermindConnectionError
from custom_components.nevermind.const import DOMAIN

USER_INPUT = {"host": "https://nevermind.example.com", "api_key": "nvm_test_key"}


async def _start_flow(hass):
    return await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )


async def test_valid_credentials_create_entry(hass):
    result = await _start_flow(hass)

    with patch(
        "custom_components.nevermind.config_flow.NevermindApiClient.async_list_ideas",
        return_value=[],
    ):
        result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == USER_INPUT["host"]
    assert result["data"] == USER_INPUT


async def test_duplicate_api_key_aborts(hass):
    result = await _start_flow(hass)
    with patch(
        "custom_components.nevermind.config_flow.NevermindApiClient.async_list_ideas",
        return_value=[],
    ):
        await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)

    result = await _start_flow(hass)
    with patch(
        "custom_components.nevermind.config_flow.NevermindApiClient.async_list_ideas",
        return_value=[],
    ):
        result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_invalid_auth_shows_form_error(hass):
    result = await _start_flow(hass)

    with patch(
        "custom_components.nevermind.config_flow.NevermindApiClient.async_list_ideas",
        side_effect=NevermindAuthError("nope"),
    ):
        result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}


async def test_cannot_connect_shows_form_error(hass):
    result = await _start_flow(hass)

    with patch(
        "custom_components.nevermind.config_flow.NevermindApiClient.async_list_ideas",
        side_effect=NevermindConnectionError("unreachable"),
    ):
        result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_unique_id_is_derived_from_api_key_not_host(hass):
    """Same key, different host, should still collide (unique_id keys off
    the API key, not the host) — reflects that the key IS the account."""
    with patch(
        "custom_components.nevermind.config_flow.NevermindApiClient.async_list_ideas",
        return_value=[],
    ):
        first = await _start_flow(hass)
        await hass.config_entries.flow.async_configure(
            first["flow_id"], {"host": "https://a.example.com", "api_key": "same-key"}
        )

        second = await _start_flow(hass)
        result = await hass.config_entries.flow.async_configure(
            second["flow_id"], {"host": "https://b.example.com", "api_key": "same-key"}
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
