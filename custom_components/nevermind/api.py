"""Thin async client for the Nevermind REST API (/api/v1)."""
from __future__ import annotations

from typing import Any

import aiohttp


class NevermindApiError(Exception):
    """Base class for anything the Nevermind API itself reported as a failure."""


class NevermindAuthError(NevermindApiError):
    """The API key was rejected (401)."""


class NevermindConnectionError(NevermindApiError):
    """The request never reached the server (timeout, DNS, refused, ...)."""


class NevermindApiClient:
    def __init__(self, session: aiohttp.ClientSession, host: str, api_key: str) -> None:
        self._session = session
        self._base = f"{host.rstrip('/')}/api/v1"
        self._headers = {"X-API-Key": api_key}

    async def _request(self, method: str, path: str, json: dict[str, Any] | None = None) -> Any:
        try:
            async with self._session.request(
                method, f"{self._base}{path}", headers=self._headers, json=json
            ) as response:
                if response.status == 401:
                    raise NevermindAuthError(f"Nevermind rejected the API key ({path})")
                if response.status >= 400:
                    raise NevermindApiError(f"Nevermind API error {response.status} on {path}")
                if response.status == 204:
                    return None
                return await response.json()
        except aiohttp.ClientError as exc:
            raise NevermindConnectionError(f"Could not reach Nevermind at {self._base}") from exc

    async def async_list_ideas(self, include_archived: bool = False) -> list[dict]:
        flag = "true" if include_archived else "false"
        return await self._request("GET", f"/ideas/?include_archived={flag}")

    async def async_create_idea(self, title: str) -> dict:
        return await self._request("POST", "/ideas/", json={"title": title})

    async def async_update_idea(self, idea_id: str, **fields: Any) -> dict:
        return await self._request("PATCH", f"/ideas/{idea_id}", json=fields)

    async def async_list_tasks(self, include_archived: bool = False) -> list[dict]:
        flag = "true" if include_archived else "false"
        return await self._request("GET", f"/tasks/?include_archived={flag}")

    async def async_update_task(self, task_id: str, **fields: Any) -> dict:
        return await self._request("PATCH", f"/tasks/{task_id}", json=fields)
