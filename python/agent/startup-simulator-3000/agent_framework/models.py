from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from dataclasses import dataclass, field
from .utils.hooks import ToolHooks, ToolSelectionHooks
from .utils.logging import AgentLogger

class ToolMetadata(BaseModel):
    """Base schema for tool metadata"""
    name: str = Field(description="Unique identifier for the tool")
    description: str = Field(description="Human-readable description of what the tool does")
    tags: List[str] = Field(description="Categories/capabilities of the tool")
    input_schema: Dict[str, Any] = Field(description="JSON schema for tool inputs")
    output_schema: Dict[str, Any] = Field(description="JSON schema for tool outputs")
    examples: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Example uses of the tool"
    )

class ToolError(BaseModel):
    """Schema for tool errors"""
    error: str = Field(description="Error message from the tool")    

class AgentMetadata(BaseModel):
    """Base schema for agent metadata"""
    name: str = Field(description="Name of the agent")
    description: str = Field(description="What the agent does")
    capabilities: List[str] = Field(description="High-level capabilities")
    tools: List[ToolMetadata] = Field(description="Tools available to this agent")
    version: str = Field(default="1.0.0", description="Version of the agent")
    custom_attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional custom metadata for the agent")
    model_config = ConfigDict(arbitrary_types_allowed=True)

class VerbosityLevel(str, Enum):
    """Controls how much information is displayed to the user"""
    NONE = "none"   # Only show final results
    LOW = "low"     # Show major steps and results
    HIGH = "high"   # Show detailed execution steps, tool selection, and reasoning

class TaskAnalysis(BaseModel):
    """Analysis of a task using chain of thought reasoning"""
    input_analysis: str = Field(
        description="Analysis of the input, identifying key requirements and constraints"
    )
    available_tools: List[str] = Field(
        description="List of tools available for the task"
    )
    tool_capabilities: Dict[str, List[str]] = Field(
        description="Mapping of tools to their key capabilities"
    )
    execution_plan: List[Dict[str, Any]] = Field(
        description="Ordered list of steps to execute, each with tool and reasoning"
    )
    requirements_coverage: Dict[str, List[str]] = Field(
        description="How the identified requirements are covered by the planned steps"
    )
    chain_of_thought: List[str] = Field(
        description="Chain of thought reasoning that led to this plan"
    )

@dataclass
class ToolContext:
    """Context object passed to tool hooks"""
    def __init__(
        self,
        task: str,
        tool_name: str,
        inputs: Dict[str, Any],
        available_tools: List[Dict[str, Any]],
        previous_tools: List[str],
        previous_results: List[Any],
        previous_errors: List[Any],
        message_history: List[Dict[str, Any]],
        agent_id: str,
        task_id: str,
        start_time: datetime,
        metadata: Dict[str, Any],
        plan: Optional[TaskAnalysis] = None
    ):
        self.task = task
        self.tool_name = tool_name
        self.inputs = inputs
        self.available_tools = available_tools
        self.previous_tools = previous_tools
        self.previous_results = previous_results
        self.previous_errors = previous_errors
        self.message_history = message_history
        self.agent_id = agent_id
        self.task_id = task_id
        self.start_time = start_time
        self.metadata = metadata
        self.plan = plan  # The agent's planning analysis

@dataclass
class Tool:
    """Model representing a tool that can be used by an agent"""
    name: str = field(metadata={"description": "Unique identifier for the tool"})
    description: str = field(metadata={"description": "Human-readable description of what the tool does"})
    tags: List[str] = field(metadata={"description": "Categories or labels for the tool's capabilities"})
    input_schema: Dict[str, Any] = field(metadata={"description": "JSON Schema defining expected input parameters"})
    output_schema: Dict[str, Any] = field(metadata={"description": "JSON Schema defining the tool's output structure"})
    hooks: Optional[ToolHooks] = field(default=None, metadata={"description": "Optional hooks for tool execution lifecycle"})

class ToolSelectionCriteria(BaseModel):
    """Criteria used for selecting a tool"""
    required_tags: List[str] = Field(
        default_factory=list,
        description="Tags that a tool must have to be considered"
    )
    preferred_tags: List[str] = Field(
        default_factory=list,
        description="Tags that are desired but not required in a tool"
    )
    context_requirements: Dict[str, Any] = Field(
        default_factory=dict,
        description="Specific contextual requirements that influence tool selection"
    )
    custom_rules: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional rules or criteria for tool selection"
    )

class ToolSelectionReasoning(BaseModel):
    """Record of the reasoning process for tool selection"""
    context: Dict[str, Any] = Field(
        description="Current context and state when the tool selection was made"
    )
    considered_tools: List[str] = Field(
        description="Names of all tools that were evaluated for selection"
    )
    selection_criteria: ToolSelectionCriteria = Field(
        description="Criteria used to evaluate and select the tool"
    )
    reasoning_steps: List[str] = Field(
        description="Detailed steps of the decision-making process"
    )
    selected_tool: str = Field(
        description="Name of the tool that was ultimately chosen"
    )
    confidence_score: float = Field(
        description="Confidence level in the tool selection (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )

class ToolCall(BaseModel):
    """Record of a tool invocation"""
    tool_name: str = Field(description="Name of the tool that was called")
    inputs: Dict[str, Any] = Field(description="Parameters passed to the tool during execution")
    outputs: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Results returned by the tool execution"
    )
    selection_reasoning: Optional[ToolSelectionReasoning] = Field(
        default=None,
        description="Reasoning process that led to selecting this tool"
    )
    execution_reasoning: str = Field(
        description="Explanation of why this tool was executed"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp when the tool was called"
    )
    success: bool = Field(
        default=True,
        description="Whether the tool execution completed successfully"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if the tool execution failed"
    )
class ExecutionStep(BaseModel):
    """Record of a single step in the agent's execution"""
    step_type: str = Field(
        description="Category or type of execution step (e.g., 'task_received', 'processing', 'completion')"
    )
    description: str = Field(
        description="Human-readable description of what happened in this step"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp when the step occurred"
    )
    tool_calls: List[ToolCall] = Field(
        default_factory=list,
        description="Tools that were called during this step"
    )
    intermediate_state: Optional[Dict[str, Any]] = Field(
        default=None,
        description="State or context information captured during this step"
    )
class TaskExecution(BaseModel):
    """Complete record of a task execution"""
    task_id: str = Field(
        description="Unique identifier for this task execution"
    )
    agent_id: str = Field(
        description="Identifier of the agent executing the task"
    )
    input: str = Field(
        description="Original input or request given to the agent"
    )
    steps: List[ExecutionStep] = Field(
        default_factory=list,
        description="Sequence of steps taken during task execution"
    )
    output: Optional[str] = Field(
        default=None,
        description="Final result or response from the task execution"
    )
    start_time: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp when task execution began"
    )
    end_time: Optional[datetime] = Field(
        default=None,
        description="UTC timestamp when task execution completed"
    )
    status: str = Field(
        default="in_progress",
        description="Current status of the task (e.g., 'in_progress', 'completed', 'failed')"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if the task execution failed"
    )

@dataclass
class AgentConfig:
    """Configuration for an agent"""
    verbosity: VerbosityLevel = field(
        default=VerbosityLevel.LOW,
        metadata={"description": "Level of detail to display to the user"}
    )
    # logger: Optional[AgentLogger] = field(
    #     default=None,
    #     metadata={"description": "Optional logger for recording agent activity"}
    # )
    tool_selection_hooks: Optional[ToolSelectionHooks] = field(
        default=None,
        metadata={"description": "Hooks for tool selection lifecycle"}
    )
    metadata: Dict[str, Any] = field(
        default_factory=dict,
        metadata={"description": "Additional configuration metadata"}
    )