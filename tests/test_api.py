"""Tests for the Nevermind API client, mocked over aiohttp via aioresponses."""
import aiohttp
import pytest
from aioresponses import aioresponses
from yarl import URL

from custom_components.nevermind.api import (
    NevermindApiClient,
    NevermindApiError,
    NevermindAuthError,
    NevermindConnectionError,
)

HOST = "https://nevermind.example.com"
BASE = f"{HOST}/api/v1"
API_KEY = "nvm_test_key"

FAKE_IDEA = {
    "id": "idea-1", "title": "Garden datacenter", "description": None, "status": "idea",
    "status_since": "2026-01-01T00:00:00+00:00", "source": "manual", "source_url": None,
    "tags": [], "notes": None, "archived": False, "archived_at": None,
    "created_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-01T00:00:00Z",
}

FAKE_TASK = {
    "id": "task-1", "title": "Buy rack", "status": "idea", "idea_id": "idea-1",
    "idea_title": "Garden datacenter", "status_since": "2026-01-01T00:00:00+00:00",
    "archived": False, "archived_at": None,
    "created_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-01T00:00:00Z",
}


@pytest.fixture
async def client():
    async with aiohttp.ClientSession() as session:
        yield NevermindApiClient(session, HOST, API_KEY)


class TestListIdeas:
    async def test_sends_api_key_and_excludes_archived_by_default(self, client):
        with aioresponses() as m:
            m.get(f"{BASE}/ideas/?include_archived=false", payload=[FAKE_IDEA])
            result = await client.async_list_ideas()

        assert result == [FAKE_IDEA]
        request = m.requests[("GET", URL(f"{BASE}/ideas/?include_archived=false"))][0]
        assert request.kwargs["headers"]["X-API-Key"] == API_KEY

    async def test_include_archived(self, client):
        with aioresponses() as m:
            m.get(f"{BASE}/ideas/?include_archived=true", payload=[FAKE_IDEA])
            result = await client.async_list_ideas(include_archived=True)
        assert result == [FAKE_IDEA]

    async def test_401_raises_auth_error(self, client):
        with aioresponses() as m:
            m.get(f"{BASE}/ideas/?include_archived=false", status=401)
            with pytest.raises(NevermindAuthError):
                await client.async_list_ideas()

    async def test_connection_error_raises_connection_error(self, client):
        with aioresponses() as m:
            m.get(f"{BASE}/ideas/?include_archived=false", exception=aiohttp.ClientConnectionError())
            with pytest.raises(NevermindConnectionError):
                await client.async_list_ideas()

    async def test_500_raises_api_error(self, client):
        with aioresponses() as m:
            m.get(f"{BASE}/ideas/?include_archived=false", status=500)
            with pytest.raises(NevermindApiError):
                await client.async_list_ideas()


class TestCreateIdea:
    async def test_posts_title(self, client):
        with aioresponses() as m:
            m.post(f"{BASE}/ideas/", payload=FAKE_IDEA, status=201)
            result = await client.async_create_idea("Garden datacenter")

        assert result == FAKE_IDEA
        request = m.requests[("POST", URL(f"{BASE}/ideas/"))][0]
        assert request.kwargs["json"] == {"title": "Garden datacenter"}


class TestUpdateIdea:
    async def test_patches_given_fields(self, client):
        with aioresponses() as m:
            m.patch(f"{BASE}/ideas/idea-1", payload={**FAKE_IDEA, "status": "done"})
            result = await client.async_update_idea("idea-1", status="done")

        assert result["status"] == "done"
        request = m.requests[("PATCH", URL(f"{BASE}/ideas/idea-1"))][0]
        assert request.kwargs["json"] == {"status": "done"}

    async def test_archive(self, client):
        with aioresponses() as m:
            m.patch(f"{BASE}/ideas/idea-1", payload={**FAKE_IDEA, "archived": True})
            await client.async_update_idea("idea-1", archived=True)

        request = m.requests[("PATCH", URL(f"{BASE}/ideas/idea-1"))][0]
        assert request.kwargs["json"] == {"archived": True}


class TestListTasks:
    async def test_excludes_archived_by_default(self, client):
        with aioresponses() as m:
            m.get(f"{BASE}/tasks/?include_archived=false", payload=[FAKE_TASK])
            result = await client.async_list_tasks()
        assert result == [FAKE_TASK]


class TestUpdateTask:
    async def test_patches_given_fields(self, client):
        with aioresponses() as m:
            m.patch(f"{BASE}/tasks/task-1", payload={**FAKE_TASK, "status": "done"})
            result = await client.async_update_task("task-1", status="done")

        assert result["status"] == "done"
        request = m.requests[("PATCH", URL(f"{BASE}/tasks/task-1"))][0]
        assert request.kwargs["json"] == {"status": "done"}
