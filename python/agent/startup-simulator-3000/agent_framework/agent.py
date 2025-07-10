from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import uuid4
from datetime import datetime
from galileo import log  # 🔍 Galileo import - this is the main Galileo logging library
from .utils.logging import AgentLogger
from .utils.tool_registry import ToolRegistry

from .models import (
    TaskExecution,
    VerbosityLevel,
    TaskAnalysis,
    ToolContext,
    ToolSelectionHooks,
    AgentConfig,
)
from .llm.base import LLMProvider
from .llm.models import LLMMessage

from .utils.formatting import (
    display_task_header,
    display_analysis,
    display_chain_of_thought,
    display_execution_plan,
    display_error,
    display_final_result,
)

from .exceptions import ToolNotFoundError, ToolExecutionError


class Agent(ABC):
    """Base class for all agents in the framework"""

    def __init__(
        self,
        *args,
        agent_id: Optional[str] = None,
        verbosity: VerbosityLevel = VerbosityLevel.LOW,
        logger: Optional[AgentLogger] = None,
        tool_selection_hooks: Optional[ToolSelectionHooks] = None,
        metadata: Optional[Dict[str, Any]] = None,
        llm_provider: Optional[LLMProvider] = None,
        **kwargs,
    ):
        self.agent_id = agent_id or str(uuid4())
        self.config = AgentConfig(
            verbosity=verbosity,
            tool_selection_hooks=tool_selection_hooks,
            metadata=metadata or {},
        )
        self.llm_provider = llm_provider
        self.tool_registry = ToolRegistry()
        self.current_task: Optional[TaskExecution] = None
        self.state: Dict[str, Any] = {}
        self.message_history: List[Dict[str, Any]] = []
        self.logger = logger
        self._current_plan: Optional[TaskAnalysis] = None

    def _setup_logger(self, logger: AgentLogger) -> None:
        """Create and set up the logger after tools are registered"""

        # Set hooks for all registered tools
        for tool in self.tool_registry.list_tools():
            tool.hooks = logger.get_tool_hooks()
        # Set tool selection hooks
        self.tool_selection_hooks = logger.get_tool_selection_hooks()

    def log_message(self, message: str, level: VerbosityLevel = VerbosityLevel.LOW) -> None:
        """Log a message if verbosity level is sufficient"""
        if self.config.verbosity.value >= level.value:
            print(message)

    def _create_tool_context(self, tool_name: str, inputs: Dict[str, Any]) -> ToolContext:
        """Create a context object for tool execution"""
        if not self.current_task:
            raise ValueError("No active task")

        return ToolContext(
            task=self.current_task.input,
            tool_name=tool_name,
            inputs=inputs,
            available_tools=self.tool_registry.get_formatted_tools(),
            previous_tools=[step.tool_name for step in self.current_task.steps],
            previous_results=[step.result for step in self.current_task.steps if step.result],
            previous_errors=[step.error for step in self.current_task.steps if step.error],
            message_history=self.message_history.copy(),
            agent_id=self.agent_id,
            task_id=self.current_task.task_id,
            start_time=self.current_task.start_time,
            metadata=self.config.metadata,
            plan=self._current_plan,  # Pass the current plan in the context
        )

    # 👀 GALILEO DECORATOR: This decorator automatically creates a span for tool execution
    # The @log decorator wraps this method and automatically logs it to Galileo
    # This means every tool call will be tracked in your Galileo dashboard
    @log(span_type="tool", name="tool_execution")
    async def call_tool(
        self,
        tool_name: str,
        inputs: Dict[str, Any],
        execution_reasoning: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a tool and log the call with selection reasoning"""
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")

        tool_context = self._create_tool_context(tool_name, inputs)

        try:
            # Call before_execution hook if available
            if tool.hooks:
                await tool.hooks.before_execution(tool_context)

            # Execute the tool using registry
            result = await self._execute_tool(tool_name, inputs)

            # Record the execution
            self.message_history.append(
                {
                    "role": "tool",
                    "tool_name": tool_name,
                    "inputs": inputs,
                    "result": result,
                    "reasoning": execution_reasoning,
                    "timestamp": datetime.now(),
                }
            )

            # Call after_execution hook if available
            if tool.hooks:
                await tool.hooks.after_execution(tool_context, result)

            return result

        except Exception as e:
            # Call after_execution hook with error if available
            if tool.hooks:
                await tool.hooks.after_execution(tool_context, None, error=e)
            raise

    async def _execute_tool(self, tool_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given inputs"""
        tool_impl = self.tool_registry.get_implementation(tool_name)
        if not tool_impl:
            raise ToolNotFoundError(f"No implementation found for tool: {tool_name}")

        try:
            tool_instance = tool_impl()
            result = await tool_instance.execute(**inputs)

            # Store result in state
            self.state.set_tool_result(tool_name, result)

            return result
        except Exception as e:
            raise ToolExecutionError(tool_name, e)

    def _create_planning_prompt(self, task: str) -> List[LLMMessage]:
        """Create prompt for task planning"""
        tools_description = "\n".join(
            [
                f"Tool: {tool.name}\n"
                f"Description: {tool.description}\n"
                f"Tags: {', '.join(tool.tags)}\n"
                f"Input Schema: {tool.input_schema}\n"
                f"Output Schema: {tool.output_schema}\n"
                for tool in self.tool_registry.get_all_tools().values()
            ]
        )

        system_prompt = (
            "You are an intelligent task planning system. Your role is to analyze tasks and create detailed execution plans.\n\n"
            "You MUST provide a complete response with ALL of the following components:\n\n"
            "1. input_analysis: A thorough analysis of the task requirements and constraints\n"
            "2. available_tools: List of all tools that could potentially be used\n"
            "3. tool_capabilities: A mapping of each available tool to its key capabilities\n"
            "4. execution_plan: A list of steps, where each step has:\n"
            "   - tool: The name of the tool to use\n"
            "   - reasoning: Why this tool was chosen for this step\n"
            "5. requirements_coverage: How each requirement is covered by which tools\n"
            "6. chain_of_thought: Your step-by-step reasoning process\n\n"
            f"Available Tools:\n{tools_description}\n\n"
            "Your response MUST be a JSON object with this EXACT structure:\n"
            "{\n"
            '  "input_analysis": "detailed analysis of the task",\n'
            '  "available_tools": ["tool1", "tool2"],\n'
            '  "tool_capabilities": {\n'
            '    "tool1": ["capability1", "capability2"],\n'
            '    "tool2": ["capability3"]\n'
            "  },\n"
            '  "execution_plan": [\n'
            '    {"tool": "tool1", "reasoning": "why tool1 is used"},\n'
            '    {"tool": "tool2", "reasoning": "why tool2 is used"}\n'
            "  ],\n"
            '  "requirements_coverage": {\n'
            '    "requirement1": ["tool1"],\n'
            '    "requirement2": ["tool1", "tool2"]\n'
            "  },\n"
            '  "chain_of_thought": [\n'
            '    "step 1 reasoning",\n'
            '    "step 2 reasoning"\n'
            "  ]\n"
            "}\n\n"
            "Ensure ALL fields are present and properly formatted. Missing fields will cause errors."
        )

        return [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(
                role="user",
                content=f"Task: {task}\n\nAnalyze this task and create a complete execution plan with ALL required fields.",
            ),
        ]

    async def plan_task(self, task: str) -> TaskAnalysis:
        """Create an execution plan for the task using chain of thought reasoning"""
        if not self.llm_provider:
            raise RuntimeError("LLM provider not configured")

        messages = self._create_planning_prompt(task)

        # Log the planning prompt
        if self.logger:
            self.logger.on_agent_start(task)

        if self.config.verbosity == VerbosityLevel.HIGH:
            display_task_header(task)

        try:
            plan: TaskAnalysis = await self.llm_provider.generate_structured(messages, TaskAnalysis, self.llm_provider.config)

            # Log the planning response
            if self.logger:
                await self.logger.on_agent_planning(plan.input_analysis)

            if self.config.verbosity == VerbosityLevel.HIGH:
                display_analysis(plan.input_analysis)
                display_chain_of_thought(plan.chain_of_thought)
                display_execution_plan(plan.execution_plan)

            return plan
        except Exception as e:
            if self.logger:
                self.logger.error(
                    "Failed to generate task plan",
                    error=str(e),
                    task=task,
                    task_id=self.current_task.task_id if self.current_task else None,
                )
            if self.config.verbosity == VerbosityLevel.HIGH:
                display_error(str(e))
            raise

    async def run(self, task: str) -> str:
        """Execute a task and return the result"""
        self.current_task = TaskExecution(
            task_id=str(uuid4()),
            agent_id=self.agent_id,
            input=task,
            start_time=datetime.now(),
            steps=[],
        )

        if self.logger:
            self.logger.on_agent_start(task)

        try:
            # Create a plan using chain of thought reasoning
            self._current_plan = await self.plan_task(task)

            # Execute each step in the plan
            results = []
            for step in self._current_plan.execution_plan:
                result = await self._execute_step(step, task, self._current_plan)
                results.append((step["tool"], result))

            # Format final result
            result = await self._format_result(task, results)
            self.current_task.output = result

            # Only call on_agent_done after all tools have completed
            if self.logger:
                await self.logger.on_agent_done(result, self.message_history)

            if self.config.verbosity == VerbosityLevel.HIGH:
                display_final_result(result)
            return result

        except Exception as e:
            self.current_task.error = str(e)
            self.current_task.status = "failed"
            raise
        finally:
            self.current_task.end_time = datetime.now()
            if self.current_task.status == "in_progress":
                self.current_task.status = "completed"
            self._current_plan = None  # Clear the plan

    async def _execute_step(self, step: Dict[str, Any], task: str, plan: TaskAnalysis) -> Any:
        """Execute a single step in the plan"""
        tool_name = step["tool"]
        if not self.tool_registry.get_tool(tool_name):
            raise ToolNotFoundError(f"Tool {tool_name} not found")

        # Map inputs for the tool
        inputs = await self._map_inputs_to_tool(tool_name, task, step.get("input_mapping", {}))

        # Create tool context once for both calls
        tool_context = self._create_tool_context(tool_name, inputs)

        # Log tool selection first
        if self.logger and (hooks := self.logger.get_tool_selection_hooks()):
            await hooks.after_selection(tool_context, tool_name, 1.0, [step["reasoning"]])

        # Then execute the tool
        result = await self.call_tool(
            tool_name=tool_name,
            inputs=inputs,
            execution_reasoning=step["reasoning"],
            context={"task": task, "plan": plan},
        )

        return result

    @abstractmethod
    async def _format_result(self, task: str, results: List[tuple[str, Dict[str, Any]]]) -> str:
        """Format the final result from tool executions"""
        pass

    async def _map_inputs_to_tool(self, tool_name: str, task: str, input_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Map inputs based on tool schema"""
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            raise ToolNotFoundError(f"Tool {tool_name} not found")

        # Get the tool's input schema
        required_inputs = tool.input_schema.get("properties", {})

        # If there's an explicit mapping from the LLM, use it
        if input_mapping:
            mapped_inputs = {}
            for input_name, value_ref in input_mapping.items():
                # Handle dot notation references (e.g., "event_finder.events")
                if "." in value_ref:
                    tool_name, field = value_ref.split(".")
                    tool_result = self.state.get_tool_result(tool_name)
                    if tool_result and isinstance(tool_result, dict):
                        mapped_inputs[input_name] = tool_result.get(field)
                else:
                    # Try to get the entire tool result
                    tool_result = self.state.get_tool_result(value_ref)
                    if tool_result is not None:
                        mapped_inputs[input_name] = tool_result
                    else:
                        # Fall back to using the value as is
                        mapped_inputs[input_name] = value_ref
            return mapped_inputs

        # Try to map inputs based on schema and state
        mapped_inputs = {}
        for input_name, input_schema in required_inputs.items():
            # Check for referenced tool outputs in schema
            if "$ref" in input_schema:
                ref_tool = input_schema.get("$ref").split("/")[-1]  # Get referenced type name
                # Look for any tool result that matches this type
                for tool_name, result in self.state.tool_results.items():
                    if result and isinstance(result, dict):  # Basic type check
                        mapped_inputs[input_name] = result
                        break
            # Otherwise try direct mapping
            elif self.state.has_tool_result(input_name):
                mapped_inputs[input_name] = self.state.get_tool_result(input_name)
            elif self.state.has_variable(input_name):
                mapped_inputs[input_name] = self.state.get_variable(input_name)
            elif input_schema.get("type") == "string":
                if input_name == "news_context" and hasattr(self, "context_data"):
                    mapped_inputs[input_name] = getattr(self, "context_data", "")
                elif input_name == "hn_context" and hasattr(self, "context_data"):
                    mapped_inputs[input_name] = getattr(self, "context_data", "")
                elif hasattr(self, "task_parameters") and input_name in self.task_parameters:
                    mapped_inputs[input_name] = self.task_parameters[input_name]
                else:
                    mapped_inputs[input_name] = task

        # For tools with no required inputs, return empty dict (all optional)
        required_fields = tool.input_schema.get("required", [])
        if not required_fields and not mapped_inputs:
            return {}  # All inputs are optional, can call with no params

        if mapped_inputs:
            return mapped_inputs

        raise ValueError(f"Could not map inputs for tool {tool_name}")
