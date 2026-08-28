# Nevermind for Home Assistant

A [HACS](https://hacs.xyz/) custom integration exposing
[Nevermind](https://github.com/proffalken/nevermind) ideas and tasks as
native Home Assistant Todo lists — addable, completable, and voice-
controllable through HA Assist.

## What you get

- **Nevermind Ideas** — a full read/write todo list. Adding an item (by UI
  or voice) creates a new Idea; completing one marks it `done`; removing one
  **archives** it in Nevermind (never deletes — abandoned ideas stay
  searchable there, same as in the Nevermind UI).
- **Nevermind Tasks** — a read/complete/remove todo list of tasks across all
  your ideas. Tasks always belong to a parent idea in Nevermind, so this
  list doesn't support creating new tasks (there's no idea to attach a
  voice-added item to) — create tasks in Nevermind itself, then manage their
  status from here.

## Requirements

- A running Nevermind instance (self-hosted or hosted) reachable from your
  Home Assistant instance.
- A personal API key, minted from the Nevermind web UI while signed in
  (Settings → API Keys). This integration authenticates with
  `X-API-Key`, not OAuth.

## Installation

### HACS

Add this repository as a custom repository in HACS, then install "Nevermind".

### Manual

Copy `custom_components/nevermind` into your Home Assistant `config/custom_components/` directory and restart.

## Setup

Settings → Devices & Services → Add Integration → **Nevermind**, then enter:

- **Host** — your Nevermind API base URL, e.g. `https://api.nevermind.example.com`
- **API Key** — the personal key from Nevermind's Settings → API Keys page

## Known limitations

- Home Assistant's todo platform only has two states (needs action /
  completed); Nevermind's five-state lifecycle (`idea → planned → active →
  done`, or `abandoned`) collapses to those two here. The full status is
  still tracked in Nevermind itself.
- Polling only, every 60 seconds — Nevermind has no push/webhook mechanism
  yet, so changes made elsewhere can take up to a minute to appear here.
