"""Tests for the two Nevermind todo entities."""
from unittest.mock import AsyncMock

import pytest
from homeassistant.components.todo import TodoItem, TodoItemStatus, TodoListEntityFeature

from custom_components.nevermind.coordinator import NevermindData, NevermindDataUpdateCoordinator
from custom_components.nevermind.todo import NevermindIdeasTodoListEntity, NevermindTasksTodoListEntity

IDEA_ACTIVE = {"id": "idea-1", "title": "Garden datacenter", "status": "active", "notes": "42U rack"}
IDEA_DONE = {"id": "idea-2", "title": "Shipped it", "status": "done", "notes": None}
TASK_OPEN = {"id": "task-1", "title": "Buy rack", "idea_id": "idea-1", "idea_title": "Garden datacenter", "status": "planned"}
TASK_ABANDONED = {"id": "task-2", "title": "Give up", "idea_id": "idea-1", "idea_title": "Garden datacenter", "status": "abandoned"}


@pytest.fixture
def api_client():
    return AsyncMock()


@pytest.fixture
def coordinator(hass, api_client):
    coord = NevermindDataUpdateCoordinator(hass, api_client)
    coord.data = NevermindData(
        ideas={"idea-1": IDEA_ACTIVE, "idea-2": IDEA_DONE},
        tasks={"task-1": TASK_OPEN, "task-2": TASK_ABANDONED},
    )
    return coord


class TestIdeasEntity:
    def test_supports_full_crud(self, coordinator):
        entity = NevermindIdeasTodoListEntity(coordinator)
        assert entity.supported_features == (
            TodoListEntityFeature.CREATE_TODO_ITEM
            | TodoListEntityFeature.UPDATE_TODO_ITEM
            | TodoListEntityFeature.DELETE_TODO_ITEM
        )

    def test_todo_items_map_status_and_fields(self, coordinator):
        entity = NevermindIdeasTodoListEntity(coordinator)
        items = {i.uid: i for i in entity.todo_items}

        assert items["idea-1"].summary == "Garden datacenter"
        assert items["idea-1"].status == TodoItemStatus.NEEDS_ACTION
        assert items["idea-1"].description == "42U rack"

        assert items["idea-2"].status == TodoItemStatus.COMPLETED

    async def test_create_calls_create_idea_and_refreshes(self, coordinator, api_client):
        entity = NevermindIdeasTodoListEntity(coordinator)
        coordinator.async_request_refresh = AsyncMock()

        await entity.async_create_todo_item(TodoItem(summary="New idea"))

        api_client.async_create_idea.assert_awaited_once_with("New idea")
        coordinator.async_request_refresh.assert_awaited_once()

    async def test_update_marks_done(self, coordinator, api_client):
        entity = NevermindIdeasTodoListEntity(coordinator)
        coordinator.async_request_refresh = AsyncMock()

        await entity.async_update_todo_item(
            TodoItem(uid="idea-1", summary="Garden datacenter", status=TodoItemStatus.COMPLETED)
        )

        api_client.async_update_idea.assert_awaited_once_with(
            "idea-1", title="Garden datacenter", status="done"
        )

    async def test_update_reopens_to_idea_status(self, coordinator, api_client):
        entity = NevermindIdeasTodoListEntity(coordinator)
        coordinator.async_request_refresh = AsyncMock()

        await entity.async_update_todo_item(
            TodoItem(uid="idea-2", summary="Shipped it", status=TodoItemStatus.NEEDS_ACTION)
        )

        api_client.async_update_idea.assert_awaited_once_with(
            "idea-2", title="Shipped it", status="idea"
        )

    async def test_delete_archives_not_deletes(self, coordinator, api_client):
        entity = NevermindIdeasTodoListEntity(coordinator)
        coordinator.async_request_refresh = AsyncMock()

        await entity.async_delete_todo_items(["idea-1"])

        api_client.async_update_idea.assert_awaited_once_with("idea-1", archived=True)
        api_client.async_delete_idea.assert_not_called()


class TestTasksEntity:
    def test_supports_update_and_delete_only(self, coordinator):
        entity = NevermindTasksTodoListEntity(coordinator)
        assert entity.supported_features == (
            TodoListEntityFeature.UPDATE_TODO_ITEM | TodoListEntityFeature.DELETE_TODO_ITEM
        )
        assert not entity.supported_features & TodoListEntityFeature.CREATE_TODO_ITEM

    def test_todo_items_include_idea_title_in_description(self, coordinator):
        entity = NevermindTasksTodoListEntity(coordinator)
        items = {i.uid: i for i in entity.todo_items}

        assert items["task-1"].summary == "Buy rack"
        assert items["task-1"].description == "Idea: Garden datacenter"
        assert items["task-1"].status == TodoItemStatus.NEEDS_ACTION
        assert items["task-2"].status == TodoItemStatus.COMPLETED

    async def test_delete_archives_not_deletes(self, coordinator, api_client):
        entity = NevermindTasksTodoListEntity(coordinator)
        coordinator.async_request_refresh = AsyncMock()

        await entity.async_delete_todo_items(["task-1"])

        api_client.async_update_task.assert_awaited_once_with("task-1", archived=True)
        api_client.async_delete_task.assert_not_called()
