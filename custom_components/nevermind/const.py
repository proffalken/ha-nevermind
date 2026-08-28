"""Constants for the Nevermind integration."""

DOMAIN = "nevermind"

DEFAULT_SCAN_INTERVAL = 60  # seconds

# Nevermind's Idea/Task status lifecycle (backend/src/nevermind/models.py
# STATUSES) — HA's todo platform only has two states, so these two sets are
# what everything else collapses onto.
COMPLETED_STATUSES = {"done", "abandoned"}
DEFAULT_INCOMPLETE_STATUS = "idea"
