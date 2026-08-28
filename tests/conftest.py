"""Shared test fixtures."""
import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Required by pytest-homeassistant-custom-component so hass can
    discover custom_components/nevermind during tests."""
    yield
