from typing import Any, Dict, List, Optional
from datetime import datetime
from .hooks import ToolContext, ToolHooks, ToolSelectionHooks
from .logging import AgentLogger

class LoggingToolHooks(ToolHooks):
    """Tool hooks that delegate to a logger"""
    
    def __init__(self, logger: AgentLogger):
        self.logger = logger
        
    async def before_execution(self, context: ToolContext) -> None:
        self.logger.info(
            f"Executing tool: {context.tool_name}",
            inputs=context.inputs,
            task_id=context.task_id
        )
        
    async def after_execution(
        self,
        context: ToolContext,
        result: Any,
        error: Optional[Exception] = None
    ) -> None:
        if error:
            self.logger.error(
                f"Tool execution failed: {context.tool_name}",
                error=str(error),
                task_id=context.task_id
            )
        else:
            self.logger.info(
                f"Tool execution completed: {context.tool_name}",
                result=result,
                task_id=context.task_id
            )

class LoggingToolSelectionHooks(ToolSelectionHooks):
    """Tool selection hooks that delegate to a logger"""
    
    def __init__(self, logger: AgentLogger):
        self.logger = logger
        
    async def after_selection(
        self,
        context: ToolContext,
        selected_tool: str,
        confidence: float,
        reasoning: List[str]
    ) -> None:
        self.logger.info(
            f"Selected tool: {selected_tool}",
            confidence=confidence,
            reasoning=reasoning,
            task_id=context.task_id
        )

def create_tool_hooks(logger: AgentLogger) -> ToolHooks:
    """Create tool hooks for a logger"""
    return LoggingToolHooks(logger)

def create_tool_selection_hooks(logger: AgentLogger) -> ToolSelectionHooks:
    """Create tool selection hooks for a logger"""
    return LoggingToolSelectionHooks(logger) 