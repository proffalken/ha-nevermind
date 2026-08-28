"""Tests for integration setup/unload."""
from unittest.mock import patch

from homeassistant.config_entries import ConfigEntryState
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nevermind.const import DOMAIN

ENTRY_DATA = {"host": "https://nevermind.example.com", "api_key": "nvm_test_key"}


async def test_setup_and_unload_entry(hass):
    entry = MockConfigEntry(domain=DOMAIN, data=ENTRY_DATA)
    entry.add_to_hass(hass)

    with (
        patch(
            "custom_components.nevermind.api.NevermindApiClient.async_list_ideas", return_value=[]
        ),
        patch(
            "custom_components.nevermind.api.NevermindApiClient.async_list_tasks", return_value=[]
        ),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        assert entry.state is ConfigEntryState.LOADED
        assert hass.states.get("todo.nevermind_ideas") is not None
        assert hass.states.get("todo.nevermind_tasks") is not None

        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.NOT_LOADED
