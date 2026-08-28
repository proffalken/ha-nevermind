"""Polling coordinator for Nevermind ideas + tasks."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NevermindApiClient, NevermindApiError, NevermindAuthError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class NevermindData:
    ideas: dict[str, dict]
    tasks: dict[str, dict]


class NevermindDataUpdateCoordinator(DataUpdateCoordinator[NevermindData]):
    def __init__(self, hass: HomeAssistant, api: NevermindApiClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> NevermindData:
        try:
            ideas, tasks = await asyncio.gather(
                self.api.async_list_ideas(include_archived=False),
                self.api.async_list_tasks(include_archived=False),
            )
        except NevermindAuthError as exc:
            raise ConfigEntryAuthFailed("Nevermind rejected the configured API key") from exc
        except NevermindApiError as exc:
            raise UpdateFailed(str(exc)) from exc

        return NevermindData(
            ideas={idea["id"]: idea for idea in ideas},
            tasks={task["id"]: task for task in tasks},
        )
