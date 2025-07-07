from typing import Dict, List, Optional, Type, TypeVar
from ..models import Tool, ToolMetadata
from ..tools.base import BaseTool

T = TypeVar('T', bound=ToolMetadata)

class ToolRegistry:
    """Central registry for tool management"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._implementations: Dict[str, Type["BaseTool"]] = {}
    
    def register(self, *, metadata: T, implementation: Type["BaseTool"]) -> None:
        """Register a tool and its implementation"""
        if metadata.name in self.tools:
            raise ValueError(f"Tool {metadata.name} is already registered")
        
        # Convert metadata to Tool model
        tool = Tool(
            name=metadata.name,
            description=metadata.description,
            tags=metadata.tags,
            input_schema=metadata.input_schema,
            output_schema=metadata.output_schema,
            hooks=None  # Hooks will be set by the agent
        )
            
        self.tools[metadata.name] = tool
        self._implementations[metadata.name] = implementation
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get tool by name"""
        return self.tools.get(name)
    
    def get_implementation(self, name: str) -> Optional[Type["BaseTool"]]:
        """Get tool implementation by name"""
        return self._implementations.get(name)
    
    def list_tools(self) -> List[Tool]:
        """Get list of all registered tools"""
        return list(self.tools.values())
    
    def get_tools_by_tags(self, tags: List[str]) -> List[Tool]:
        """Get tools that have all specified tags"""
        return [
            tool for tool in self.tools.values()
            if all(tag in tool.tags for tag in tags)
        ] 