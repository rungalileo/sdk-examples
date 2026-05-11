# src/research_crew/crew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List


@CrewBase
class ResearchCrew:
    """Research crew for comprehensive topic analysis and reporting"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def researcher(self) -> Agent:
        return Agent(config=self.agents_config["researcher"], verbose=True, tools=[SerperDevTool()])  # type: ignore[index]

    @agent
    def analyst(self) -> Agent:
        return Agent(config=self.agents_config["analyst"], verbose=True)  # type: ignore[index]

    @task
    def research_task(self) -> Task:
        return Task(config=self.tasks_config["research_task"])  # type: ignore[index]

    @task
    def analysis_task(self) -> Task:
        return Task(config=self.tasks_config["analysis_task"], output_file="output/report.md")  # type: ignore[index]

    @crew
    def crew(self) -> Crew:
        """Creates the research crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
