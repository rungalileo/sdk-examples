class AgentError(Exception):
    """Base class for agent framework exceptions"""
    pass

class ToolError(AgentError):
    """Base class for tool-related errors"""
    pass

class ToolNotFoundError(ToolError):
    """Raised when a requested tool is not found"""
    pass

class ToolExecutionError(ToolError):
    """Raised when a tool execution fails"""
    def __init__(self, tool_name: str, original_error: Exception):
        self.tool_name = tool_name
        self.original_error = original_error
        super().__init__(f"Tool {tool_name} execution failed: {str(original_error)}")

class ConfigurationError(AgentError):
    """Raised when there's a configuration problem"""
    pass

class PlanningError(AgentError):
    """Raised when task planning fails"""
    pass

class StateError(AgentError):
    """Raised when there's a state-related error"""
    pass 