import os
from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai.tools import BaseTool
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from my_first_crewai.tools.gaode_sse_mcp import get_mcp_gaode_see_tools
from my_first_crewai.tools.travel_tools import IPLocationTool, WeatherTool, TrafficTool, TimeTool, ImageSearchTool
@CrewBase
class MyFirstCrewai():
    """MyFirstCrewai crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    #personalized_activity_planner
    #restaurant_scout
    #itinerary_compiler

    llm = LLM(
        model="deepseek/deepseek-chat",
        stream=True,
        temperature=0.9,
        #api_base="https://api.deepseek.com"    
    )
    gaode_tools:List[BaseTool] = get_mcp_gaode_see_tools()
    tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(),
                IPLocationTool(),
                WeatherTool(),
                #TrafficTool(),
                TimeTool(),
                #ImageSearchTool()               
            ]
    tools.extend(gaode_tools)

    @agent
    def personalized_activity_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['personalized_activity_planner'], # type: ignore[index]            
            verbose=True,
            llm=self.llm,
            tools=self.tools,
        )
    
    @agent
    def restaurant_scout(self) -> Agent:
        return Agent(
            config=self.agents_config['restaurant_scout'], # type: ignore[index]
            verbose=True,
            llm=self.llm
        )
    
    @agent
    def itinerary_compiler(self) -> Agent:
        return Agent(
            config=self.agents_config['itinerary_compiler'], # type: ignore[index]
            verbose=True,
            llm=self.llm
        )
    
    @agent
    def gaode_picture_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['gaode_picture_agent'], # type: ignore[index]
            verbose=True,
            llm=self.llm,
            tools=self.gaode_tools
        )
    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task

    #personalized_activity_planning_task
    #restaurant_scenic_location_scout_task
    #itinerary_compilation_task
    @task
    def personalized_activity_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config['personalized_activity_planning_task'], # type: ignore[index]
            agent=self.personalized_activity_planner()
        )
    
    @task
    def gaode_picture_task(self) -> Task:
        return Task(
            config=self.tasks_config['gaode_picture_task'], # type: ignore[index]
            agent=self.gaode_picture_agent()
        )
    
    @task
    def restaurant_scenic_location_scout_task(self) -> Task:
        return Task(
            config=self.tasks_config['restaurant_scenic_location_scout_task'], # type: ignore[index]
            agent=self.restaurant_scout()
        )

    @task
    def itinerary_compilation_task(self) -> Task:
        return Task(
            config=self.tasks_config['itinerary_compilation_task'], # type: ignore[index]
            agent=self.itinerary_compiler(),
            tools=[SerperDevTool(),
                ScrapeWebsiteTool()],
            output_file='report.md'
        )



    @crew
    def crew(self) -> Crew:
        """Creates the MyFirstCrewai crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
