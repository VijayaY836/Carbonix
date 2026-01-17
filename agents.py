from crewai import Agent, Task, Crew, Process
from tools import LogisticsTools

# Agent 1: The Green Auditor
carbon_agent = Agent(
    role='Carbon Emission Specialist',
    goal='Minimize CO2 footprint by selecting slow-steaming or greener modes.',
    backstory='A radical environmental scientist who prioritizes the planet over profit.',
    verbose=True
)

# Agent 2: The Profit Optimizer
cost_agent = Agent(
    role='Commercial Logistics Lead',
    goal='Maximize delivery speed and minimize transport costs.',
    backstory='A cutthroat logistics veteran who hates delays and wasted fuel.',
    verbose=True
)

def initiate_swarm(origin, dest, weight):
    task = Task(
        description=f"Route shipment from {origin} to {dest} ({weight} tons). Compare Sea vs Rail. Factor in a $100/ton Carbon Tax.",
        expected_output="A table comparing routes with a final 'Agentic Recommendation'.",
        agent=carbon_agent
    )

    crew = Crew(
        agents=[carbon_agent, cost_agent],
        tasks=[task],
        process=Process.sequential
    )
    return crew.kickoff()