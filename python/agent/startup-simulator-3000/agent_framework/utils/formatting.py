"""Utilities for formatting and displaying output"""
import json
from typing import Any, Dict, List
from rich.console import Console
from rich.panel import Panel
from rich.json import JSON
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text
from rich.syntax import Syntax

console = Console()

def format_json(data: Any) -> str:
    """Format JSON data for pretty printing"""
    return json.dumps(data, indent=2, default=str)

def display_task_header(task: str):
    """Display a task header"""
    console.print(Panel(
        f"[bold blue]Task:[/bold blue] {task}",
        title="🤖 Agent Task",
        border_style="blue"
    ))

def display_analysis(analysis: str):
    """Display task analysis"""
    console.print(Panel(
        Markdown(analysis),
        title="📋 Task Analysis",
        border_style="green"
    ))

def display_chain_of_thought(steps: List[str]):
    """Display chain of thought reasoning"""
    table = Table(title="🤔 Chain of Thought", show_header=False, border_style="cyan")
    table.add_column("Step", style="dim")
    table.add_column("Reasoning")
    
    for i, step in enumerate(steps, 1):
        table.add_row(f"Step {i}", Markdown(step))
    
    console.print(table)

def display_execution_plan(plan: List[Dict[str, Any]]):
    """Display execution plan"""
    table = Table(title="📝 Execution Plan", border_style="magenta")
    table.add_column("Tool", style="bold cyan")
    table.add_column("Reasoning")
    
    for step in plan:
        table.add_row(step["tool"], Markdown(step["reasoning"]))
    
    console.print(table)

def display_tool_result(tool_name: str, result: Dict[str, Any]):
    """Display tool execution result"""
    if isinstance(result, (dict, list)):
        result_display = Syntax(
            format_json(result),
            "json",
            theme="monokai",
            word_wrap=True
        )
    else:
        result_display = Markdown(str(result))
    
    console.print(Panel(
        result_display,
        title=f"🔧 {tool_name} Result",
        border_style="yellow"
    ))

def display_final_result(result: str):
    """Display final combined result"""
    console.print(Panel(
        Markdown(result),
        title="✨ Final Result",
        border_style="green",
        padding=(1, 2)
    ))

def display_error(error: str):
    """Display error message"""
    console.print(Panel(
        f"[bold red]Error:[/bold red] {error}",
        title="❌ Error",
        border_style="red"
    ))
