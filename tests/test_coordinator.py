"""Tests for NevermindDataUpdateCoordinator."""
from unittest.mock import AsyncMock

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.nevermind.api import NevermindApiError, NevermindAuthError
from custom_components.nevermind.coordinator import NevermindDataUpdateCoordinator

FAKE_IDEA = {"id": "idea-1", "title": "Garden datacenter", "status": "idea"}
FAKE_TASK = {"id": "task-1", "title": "Buy rack", "idea_id": "idea-1", "status": "idea"}


@pytest.fixture
def api_client():
    client = AsyncMock()
    client.async_list_ideas.return_value = [FAKE_IDEA]
    client.async_list_tasks.return_value = [FAKE_TASK]
    return client


async def test_fetches_and_indexes_ideas_and_tasks_by_id(hass, api_client):
    coordinator = NevermindDataUpdateCoordinator(hass, api_client)
    data = await coordinator._async_update_data()

    api_client.async_list_ideas.assert_awaited_once_with(include_archived=False)
    api_client.async_list_tasks.assert_awaited_once_with(include_archived=False)
    assert data.ideas == {"idea-1": FAKE_IDEA}
    assert data.tasks == {"task-1": FAKE_TASK}


async def test_auth_error_raises_config_entry_auth_failed(hass, api_client):
    from homeassistant.exceptions import ConfigEntryAuthFailed

    api_client.async_list_ideas.side_effect = NevermindAuthError("nope")
    coordinator = NevermindDataUpdateCoordinator(hass, api_client)

    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()


async def test_other_api_error_raises_update_failed(hass, api_client):
    api_client.async_list_tasks.side_effect = NevermindApiError("boom")
    coordinator = NevermindDataUpdateCoordinator(hass, api_client)

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
