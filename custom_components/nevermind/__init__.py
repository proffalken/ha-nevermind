"""The Nevermind integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NevermindApiClient
from .coordinator import NevermindDataUpdateCoordinator

PLATFORMS = [Platform.TODO]

type NevermindConfigEntry = ConfigEntry[NevermindDataUpdateCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: NevermindConfigEntry) -> bool:
    api = NevermindApiClient(
        async_get_clientsession(hass), entry.data[CONF_HOST], entry.data[CONF_API_KEY]
    )
    coordinator = NevermindDataUpdateCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: NevermindConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
