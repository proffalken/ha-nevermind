"""Todo platform: Nevermind ideas and tasks as Home Assistant todo lists."""
from __future__ import annotations

from homeassistant.components.todo import TodoItem, TodoItemStatus, TodoListEntity, TodoListEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import COMPLETED_STATUSES, DEFAULT_INCOMPLETE_STATUS, DOMAIN
from .coordinator import NevermindDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: NevermindDataUpdateCoordinator = entry.runtime_data
    async_add_entities(
        [NevermindIdeasTodoListEntity(coordinator), NevermindTasksTodoListEntity(coordinator)]
    )


def _status_to_todo(status: str) -> TodoItemStatus:
    return TodoItemStatus.COMPLETED if status in COMPLETED_STATUSES else TodoItemStatus.NEEDS_ACTION


def _todo_status_to_nevermind(status: TodoItemStatus | None) -> str:
    return "done" if status == TodoItemStatus.COMPLETED else DEFAULT_INCOMPLETE_STATUS


class NevermindIdeasTodoListEntity(CoordinatorEntity[NevermindDataUpdateCoordinator], TodoListEntity):
    """Every Nevermind idea, full CRUD. Adding an item creates a new idea;
    removing one archives it (Nevermind never deletes ideas from here)."""

    _attr_supported_features = (
        TodoListEntityFeature.CREATE_TODO_ITEM
        | TodoListEntityFeature.UPDATE_TODO_ITEM
        | TodoListEntityFeature.DELETE_TODO_ITEM
    )
    _attr_name = "Nevermind Ideas"
    _attr_unique_id = f"{DOMAIN}_ideas"

    @property
    def todo_items(self) -> list[TodoItem]:
        return [
            TodoItem(
                uid=idea["id"],
                summary=idea["title"],
                status=_status_to_todo(idea["status"]),
                description=idea.get("notes"),
            )
            for idea in self.coordinator.data.ideas.values()
        ]

    async def async_create_todo_item(self, item: TodoItem) -> None:
        await self.coordinator.api.async_create_idea(item.summary)
        await self.coordinator.async_request_refresh()

    async def async_update_todo_item(self, item: TodoItem) -> None:
        await self.coordinator.api.async_update_idea(
            item.uid, title=item.summary, status=_todo_status_to_nevermind(item.status)
        )
        await self.coordinator.async_request_refresh()

    async def async_delete_todo_items(self, uids: list[str]) -> None:
        for uid in uids:
            await self.coordinator.api.async_update_idea(uid, archived=True)
        await self.coordinator.async_request_refresh()


class NevermindTasksTodoListEntity(CoordinatorEntity[NevermindDataUpdateCoordinator], TodoListEntity):
    """Every Nevermind task across all ideas. Update/complete/remove only —
    creating a task needs a parent idea, which a bare title can't supply."""

    _attr_supported_features = (
        TodoListEntityFeature.UPDATE_TODO_ITEM | TodoListEntityFeature.DELETE_TODO_ITEM
    )
    _attr_name = "Nevermind Tasks"
    _attr_unique_id = f"{DOMAIN}_tasks"

    @property
    def todo_items(self) -> list[TodoItem]:
        return [
            TodoItem(
                uid=task["id"],
                summary=task["title"],
                status=_status_to_todo(task["status"]),
                description=f"Idea: {task['idea_title']}" if task.get("idea_title") else None,
            )
            for task in self.coordinator.data.tasks.values()
        ]

    async def async_update_todo_item(self, item: TodoItem) -> None:
        await self.coordinator.api.async_update_task(
            item.uid, title=item.summary, status=_todo_status_to_nevermind(item.status)
        )
        await self.coordinator.async_request_refresh()

    async def async_delete_todo_items(self, uids: list[str]) -> None:
        for uid in uids:
            await self.coordinator.api.async_update_task(uid, archived=True)
        await self.coordinator.async_request_refresh()
