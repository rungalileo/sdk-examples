"""CrewAI Research Agent with Planning Feature"""

import os
import warnings
import argparse
from datetime import datetime
from crewai import LLM, Agent, Task, Crew
from crewai_tools import EXASearchTool
from dotenv import load_dotenv
from tools import TodoListTool
from galileo.handlers.crewai.handler import CrewAIEventListener

# Load environment variables
load_dotenv("../.env")

CrewAIEventListener()


# Initialize tools and models
openai_model = LLM(model="openai/gpt-4.1-mini", temperature=0.1, api_key=os.getenv("OPENAI_API_KEY"))
exa_tool = EXASearchTool(api_key=os.getenv("EXA_API_KEY"))
todo_tool = TodoListTool()

# Create agents
analyst = Agent(
    role="Research Specialist",
    goal="Conduct detailed research on {topic} using the latest information as of {todays_date}. Think about the best questions to ask to get the most relevant information. Focus on technical details. Think critically and find deep insights. Use the TodoListTool to track your writing progress. Mark subtasks complete as you finish each section.",
    backstory="You are an expert at web research.",
    llm=openai_model,
    tools=[exa_tool, todo_tool],
    reasoning=True,
    max_reasoning_attempts=3,
    # verbose=True
)

reporter = Agent(
    role="Report Specialist",
    goal="Generate a detailed report on {topic} using the latest information as of {todays_date}. Use the TodoListTool to track your writing progress. Mark subtasks complete as you finish each section.",
    backstory="You are an expert at research report writing with years of experience creating executive summaries and detailed technical reports.",
    llm=openai_model,
    tools=[todo_tool],
    # verbose=True
)

reviewer = Agent(
    role="Report Review Specialist",
    goal="""Review and validate the quality of reports on {topic}.

    CRITICAL: For each issue found, ADD a specific improvement task to the TodoList using the 'add' operation.
    Each task should be clear and actionable for the Report Specialist to complete.

    Example tasks to add:
    - "Improve executive summary clarity by adding specific metrics"
    - "Add citations for claim about X in section Y"
    - "Expand technical analysis in section Z with more details"

    Only mark the report as APPROVED when all quality standards are met.""",
    backstory="You are a senior editor and quality assurance expert with decades of experience reviewing executive reports. You have high standards and provide actionable feedback by creating specific improvement tasks.",
    llm=openai_model,
    tools=[todo_tool],
    reasoning=True,
    max_reasoning_attempts=2,
    # verbose=True
)

# Create tasks
analysis_task = Task(
    description="""Research and analyze the recent trends on {topic}.""",
    expected_output="Comprehensive research findings with key insights, trends, and technical details.",
    agent=analyst,
    # async_execution=True,  # Disabled to ensure proper sequential execution
    # verbose=True
)

report_task = Task(
    description="""Generate a detailed, well-structured report on {topic} based on the research findings.""",
    expected_output="A polished executive report with clear sections: Executive Summary, Key Findings, Detailed Analysis, and Conclusions.",
    agent=reporter,
    context=[analysis_task],
    # verbose=True
)

review_task = Task(
    description="""Review the report on {topic} for quality, accuracy, clarity, and completeness.

    WORKFLOW:
    1. First, use TodoListTool with operation='get_list' to see current todo status
    2. Read the report carefully and evaluate:
       - Clarity and readability for C-suite executives
       - Accuracy of information and citations
       - Completeness of coverage
       - Structure and flow
       - Technical depth vs. accessibility balance

    3. For EACH issue/improvement needed, use TodoListTool with operation='add' to create a specific task:
       - title: Clear, actionable improvement (e.g., "Add citation for AGI benchmark claim")
       - description: Detailed explanation of what needs to be done

    4. After adding all improvement tasks, provide assessment:
       - If NO tasks added: Mark as APPROVED
       - If tasks added: Mark as NEEDS REVISION with count of improvement tasks added

    The Report Specialist will then work through the TodoList to complete all improvements.""",
    expected_output="""Review result stating:
    - APPROVED: Report meets all standards, no improvements needed
    - NEEDS REVISION: X improvement tasks added to TodoList for Report Specialist to complete""",
    agent=reviewer,
    context=[report_task],
    # verbose=True
)

revision_task = Task(
    description="""Work through the TodoList to improve the report based on reviewer feedback.

    WORKFLOW:
    1. Use TodoListTool with operation='get_list' to see all pending improvement tasks
    2. For EACH pending task:
       a. Read the task title and description carefully
       b. Make the specific improvement to the report
       c. Use TodoListTool with operation='mark_complete' and the task's todo_id to mark it done
       d. The tool will automatically print the updated todo list after each completion
    3. Continue until ALL tasks are marked complete
    4. Use TodoListTool with operation='get_list' one final time to confirm all tasks are done

    Only finish when the TodoList shows all tasks as COMPLETED.""",
    expected_output="""Improved report with all reviewer feedback addressed.
    TodoList should show all improvement tasks marked as COMPLETED.""",
    agent=reporter,
    context=[report_task, review_task],
    # verbose=True
)

# Create a crew with planning enabled
crew = Crew(
    agents=[analyst, reporter, reviewer],
    tasks=[analysis_task, report_task, review_task, revision_task],
    planning=True,
    planning_llm=openai_model,
    verbose=True,
)

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="CrewAI Research Agent - Generate comprehensive research reports on any topic",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "AI trends in 2025"
  python main.py "Quantum computing breakthroughs" --date "December 1, 2025"
  python main.py --topic "Climate change solutions"
  python main.py "LLM reasoning" --clear-todos  # Clear todo list before starting
        """,
    )

    parser.add_argument(
        "topic",
        nargs="?",  # Make positional argument optional
        help="The topic to research and generate a report about",
    )

    parser.add_argument(
        "--topic",
        "-t",
        dest="topic_flag",
        help="Alternative way to specify the topic using a flag",
    )

    parser.add_argument(
        "--date",
        "-d",
        default=datetime.now().strftime("%B %d, %Y"),
        help="The date context for the research (default: today's date)",
    )

    parser.add_argument(
        "--clear-todos",
        action="store_true",
        help="Clear the todo list before starting (useful for fresh runs)",
    )

    # Parse arguments
    args = parser.parse_args()

    # Determine which topic to use (positional or flag)
    topic = args.topic or args.topic_flag

    if not topic:
        print("Error: Please provide a topic to research.")
        print("\nUsage examples:")
        print('  python main.py "AI trends in 2025"')
        print('  python main.py --topic "Quantum computing"')
        parser.print_help()
        exit(1)

    # Clear todos if requested
    if args.clear_todos:
        TodoListTool.clear_all_todos()
        print("✨ Todo list cleared for fresh start")

    print(f"\nStarting research on: {topic}")
    print(f"Date context: {args.date}")
    print("-" * 80)

    # Run the crew
    result = crew.kickoff(
        inputs={
            "topic": topic,
            "todays_date": args.date,
        }
    )

    # Print the result
    print("\n" + "=" * 80)
    print("FINAL REPORT")
    print("=" * 80)
    print(result.raw)
