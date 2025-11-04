"""Custom tools for CrewAI agents"""

from typing import Type, Dict, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

# Module-level storage for todos to avoid Pydantic attribute conflicts
# This ensures all instances share the same todo list
SHARED_TODOS: Dict[str, "TodoItem"] = {}


class TodoItem(BaseModel):
    """Todo item model"""

    id: str
    title: str
    description: Optional[str] = ""
    completed: bool = False
    created_at: str
    updated_at: str


class TodoListInput(BaseModel):
    """Input schema for TodoListTool operations"""

    operation: str = Field(
        ...,
        description="Operation to perform: get_list, add, remove, update, mark_complete, mark_uncomplete",
    )

    # For add operation
    title: Optional[str] = Field(None, description="Title for new todo item")
    description: Optional[str] = Field(None, description="Description for new todo item")

    # For remove, update, mark_complete, mark_uncomplete operations
    todo_id: Optional[str] = Field(None, description="ID of todo item to modify")

    # For update operation
    new_title: Optional[str] = Field(None, description="New title for todo item")
    new_description: Optional[str] = Field(None, description="New description for todo item")


class TodoListTool(BaseTool):
    name: str = "TodoListManager"
    description: str = """
    Comprehensive todo list management tool for planning agents.
    Supports operations: get_list, add, remove, update, mark_complete, mark_uncomplete.
    Use this tool to manage tasks, track progress, and organize work items.
    """
    args_schema: Type[BaseModel] = TodoListInput

    @property
    def todos(self) -> Dict[str, TodoItem]:
        """Access the shared todo list"""
        # Use the module-level variable
        global SHARED_TODOS
        return SHARED_TODOS

    @todos.setter
    def todos(self, value: Dict[str, TodoItem]):
        """Update the shared todo list"""
        # Update the module-level variable
        global SHARED_TODOS
        SHARED_TODOS = value

    def _run(
        self,
        operation: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        todo_id: Optional[str] = None,
        new_title: Optional[str] = None,
        new_description: Optional[str] = None,
    ) -> str:
        """Execute todo list operations"""

        try:
            if operation == "get_list":
                return self._get_list()
            elif operation == "add":
                if not title:
                    return "Error: Title is required for adding a todo item"
                return self._add_todo(title, description or "")
            elif operation == "remove":
                if not todo_id:
                    return "Error: todo_id is required for removing a todo item"
                return self._remove_todo(todo_id)
            elif operation == "update":
                if not todo_id:
                    return "Error: todo_id is required for updating a todo item"
                return self._update_todo(todo_id, new_title, new_description)
            elif operation == "mark_complete":
                if not todo_id:
                    return "Error: todo_id is required for marking todo as complete"
                return self._mark_complete(todo_id)
            elif operation == "mark_uncomplete":
                if not todo_id:
                    return "Error: todo_id is required for marking todo as uncomplete"
                return self._mark_uncomplete(todo_id)
            else:
                return f"Error: Unknown operation '{operation}'. Available operations: get_list, add, remove, update, mark_complete, mark_uncomplete"

        except Exception as e:
            return f"Error executing operation '{operation}': {str(e)}"

    def _get_list(self) -> str:
        """Get all todo items"""
        if not self.todos:
            return "Todo list is empty."

        result = "=== TODO LIST ===\n"
        completed_todos = []
        pending_todos = []

        for todo in self.todos.values():
            status = "✅" if todo.completed else "⭕"
            todo_info = f"{status} [{todo.id}] {todo.title}"
            if todo.description:
                todo_info += f" - {todo.description}"

            if todo.completed:
                completed_todos.append(todo_info)
            else:
                pending_todos.append(todo_info)

        if pending_todos:
            result += "\nPENDING:\n" + "\n".join(pending_todos)
        if completed_todos:
            result += "\n\nCOMPLETED:\n" + "\n".join(completed_todos)

        result += f"\n\nTotal: {len(self.todos)} items ({len(pending_todos)} pending, {len(completed_todos)} completed)"
        return result

    def _add_todo(self, title: str, description: str) -> str:
        """Add new todo item"""
        todo_id = str(uuid.uuid4())[:8]  # Short ID
        current_time = datetime.now().isoformat()

        new_todo = TodoItem(
            id=todo_id,
            title=title,
            description=description,
            completed=False,
            created_at=current_time,
            updated_at=current_time,
        )

        self.todos[todo_id] = new_todo
        result = f"✅ Added todo item: [{todo_id}] {title}\n\n"
        result += self._get_list()
        return result

    def _remove_todo(self, todo_id: str) -> str:
        """Remove todo item"""
        if todo_id not in self.todos:
            return f"❌ Todo item with ID '{todo_id}' not found"

        removed_todo = self.todos.pop(todo_id)
        result = f"🗑️ Removed todo item: [{todo_id}] {removed_todo.title}\n\n"
        result += self._get_list()
        return result

    def _update_todo(self, todo_id: str, new_title: Optional[str], new_description: Optional[str]) -> str:
        """Update todo item"""
        if todo_id not in self.todos:
            return f"❌ Todo item with ID '{todo_id}' not found"

        todo = self.todos[todo_id]
        changes = []

        if new_title:
            old_title = todo.title
            todo.title = new_title
            changes.append(f"title: '{old_title}' → '{new_title}'")

        if new_description is not None:
            old_desc = todo.description
            todo.description = new_description
            changes.append(f"description: '{old_desc}' → '{new_description}'")

        if changes:
            todo.updated_at = datetime.now().isoformat()
            result = f"📝 Updated todo [{todo_id}]: {', '.join(changes)}\n\n"
        else:
            result = f"ℹ️ No changes made to todo [{todo_id}]\n\n"

        result += self._get_list()
        return result

    def _mark_complete(self, todo_id: str) -> str:
        """Mark todo as complete"""
        if todo_id not in self.todos:
            return f"❌ Todo item with ID '{todo_id}' not found"

        todo = self.todos[todo_id]
        if todo.completed:
            result = f"ℹ️ Todo [{todo_id}] '{todo.title}' is already completed\n\n"
        else:
            todo.completed = True
            todo.updated_at = datetime.now().isoformat()
            result = f"✅ Marked todo as complete: [{todo_id}] {todo.title}\n\n"

        result += self._get_list()
        return result

    def _mark_uncomplete(self, todo_id: str) -> str:
        """Mark todo as uncomplete"""
        if todo_id not in self.todos:
            return f"❌ Todo item with ID '{todo_id}' not found"

        todo = self.todos[todo_id]
        if not todo.completed:
            result = f"ℹ️ Todo [{todo_id}] '{todo.title}' is already pending\n\n"
        else:
            todo.completed = False
            todo.updated_at = datetime.now().isoformat()
            result = f"⭕ Marked todo as pending: [{todo_id}] {todo.title}\n\n"

        result += self._get_list()
        return result

    @classmethod
    def clear_all_todos(cls):
        """Clear all todos from the shared storage (useful for testing)"""
        global SHARED_TODOS
        SHARED_TODOS = {}
        return "✨ All todos have been cleared"
