from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class AgentState:
    """Container for agent state management"""
    
    # General state
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # Tool execution state
    tool_results: Dict[str, Any] = field(default_factory=dict)
    last_tool: Optional[str] = None
    
    # Task state
    task_start_time: Optional[datetime] = None
    task_variables: Dict[str, Any] = field(default_factory=dict)
    
    def has_variable(self, name: str) -> bool:
        """Check if a variable exists in state"""
        return name in self.variables
    
    def set_variable(self, name: str, value: Any) -> None:
        """Set a state variable"""
        self.variables[name] = value
    
    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get a state variable"""
        return self.variables.get(name, default)
    
    def set_tool_result(self, tool_name: str, result: Any) -> None:
        """Store a tool execution result"""
        self.tool_results[tool_name] = result
        self.last_tool = tool_name
    
    def get_tool_result(self, tool_name: str, default: Any = None) -> Any:
        """Get a tool execution result"""
        return self.tool_results.get(tool_name, default)
    
    def get_last_tool_result(self, default: Any = None) -> Any:
        """Get the result of the last executed tool"""
        if not self.last_tool:
            return default
        return self.tool_results.get(self.last_tool, default)
    
    def clear(self) -> None:
        """Clear all state"""
        self.variables.clear()
        self.tool_results.clear()
        self.last_tool = None
        self.task_variables.clear()
        self.task_start_time = None
    
    def has_tool_result(self, tool_name: str) -> bool:
        """Check if a tool result exists"""
        return tool_name in self.tool_results 