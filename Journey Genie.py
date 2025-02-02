# -*- coding: utf-8 -*-


!pip install crewai crewai_tools==0.1.6 langchain_community==0.0.29

from crewai import Crew, Process, Agent, Task

# Commented out IPython magic to ensure Python compatibility.
# %pip -q install groq
# %pip -q install langchain-groq

from google.colab import userdata
import os
os.environ["SERPER_API_KEY"]=userdata.get('serper')
os.environ["GROQ_API_KEY"]=userdata.get('groq')
from langchain_groq import ChatGroq
llm = ChatGroq(temperature=0, model_name="llama3-70b-8192")

from crewai_tools import ScrapeWebsiteTool, SerperDevTool

search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

bookings_agent = Agent(
    role="Senior travel booking consultant",
    goal="Analyzes locations and suggests an appropriate mode of travel and stay option within the budget and time frame",
    backstory="Specialized in ticket booking this agent advises travel tickets and "
               "stay tickets it is equipped with various tools for the same task",
    verbose=True,
    allow_delegation=True,
    tools = [scrape_tool, search_tool],
    llm=llm
)

tour_guide_agent= Agent(
    role="Senior tour planner",
    goal="Analyzes the travel location and finds popular places to visit in given time and budget",
    backstory="Specialized in planning tours the agent manages schedules and also finds good places to visit"
               " at the location and nearby keeping constraints in mind."
               "It is equipped with various tools for the same.",
    verbose=True,
    allow_delegation=True,
    tools = [scrape_tool, search_tool],
    llm=llm
)

budget_and_time_agent= Agent(
    role="Senior planner and budget optimizer",
    goal="Checks if the given plan suits in constraints of time and budget,"
          "prepares an intenary in a manner that can be presented to the customer",
    backstory="Specialized in planning tours the agent manages schedules keeping budget in mind and time in check."
               "It carefully drafts a blog presented to customer for the travel plan/"
               "It is equipped with various tools for the same.",
    verbose=True,
    allow_delegation=True,
    tools = [scrape_tool, search_tool],
    llm=llm
)

bookings_agent_task = Task(
    description=(
        "finds travel tickets for {from} to {to} in given {travel_budget} which are comfortable and has least number of layovers"
    ),
    expected_output=(
        "Travel modes and options for reaching location"
        "based on given constraints of time and money"
    ),
    agent=bookings_agent,
)

tour_guide_task = Task(
    description=(
        "finds locations to visit at {to} within given {budget} and {preferred} type of customer choice of activities"
    ),
    expected_output=(
        "a list of all locations to visit near given place suiting constraints of time and money and choice of customer"
    ),
    agent=tour_guide_agent,
)

budget_and_time_task = Task(
    description=(
        "check if given locations and travel,stay fall in given {budget} and {travel_budget} and {no_of_days} and prepare a presentable itenary for the same as per customer choice of {preferred}"
    ),
    expected_output=(
        "an itenary that can be presented to customer"
    ),
    agent=budget_and_time_agent,
)

from crewai import Crew, Process
travel_planner_crew = Crew(
    agents=[bookings_agent,
            tour_guide_agent,
            budget_and_time_agent],

    tasks=[bookings_agent_task,
           tour_guide_task,
           budget_and_time_task],

    manager_llm=llm,
    process=Process.hierarchical,
    verbose=True
)

travel_plan_inputs={
    'from':'jaipur,rajasthan',
    'to':'mumbai,india',
    'budget':'inr 20000 per person',
    'travel_budget':'inr 5000 per person',
    'no_of_days':'4',
    'preferred':'cultural and modern'
}

result=travel_planner_crew.kickoff(inputs=travel_plan_inputs)
