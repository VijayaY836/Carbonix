from crewai import Agent, Task, Crew, Process
from tools import LogisticsTools

# Agent 1: The Green Auditor
carbon_agent = Agent(
    role='Carbon Emission Specialist',
    goal='Minimize CO2 footprint by selecting greener transport modes and carbon-efficient routing.',
    backstory="""You are a radical environmental scientist who prioritizes planetary health. 
    You analyze emissions data, advocate for slow-steaming and rail transport, and calculate 
    the true environmental cost of every logistics decision. Carbon tax is your weapon.""",
    tools=[
        LogisticsTools.calculate_carbon,
        LogisticsTools.compare_routes,
        LogisticsTools.get_port_congestion
    ],
    verbose=True,
    allow_delegation=False
)

# Agent 2: The Profit Optimizer
cost_agent = Agent(
    role='Commercial Logistics Lead',
    goal='Maximize delivery speed while minimizing transport costs and delays.',
    backstory="""You are a cutthroat logistics veteran who has orchestrated thousands of shipments. 
    Time is money. Delays cost millions. You optimize for fastest routes, lowest base costs, 
    and hate carbon taxes eating into margins. Speed and efficiency are your religion.""",
    tools=[
        LogisticsTools.calculate_carbon,
        LogisticsTools.compare_routes,
        LogisticsTools.get_port_congestion
    ],
    verbose=True,
    allow_delegation=False
)

# Agent 3: Risk Assessor
risk_agent = Agent(
    role='Supply Chain Risk Manager',
    goal='Identify and mitigate risks including port congestion, delays, and reliability issues.',
    backstory="""You are a paranoid but brilliant risk analyst. You've seen supply chains 
    collapse from port strikes, congestion, and weather. You assess every variable that could 
    derail a shipment and provide contingency recommendations.""",
    tools=[
        LogisticsTools.get_port_congestion,
        LogisticsTools.compare_routes
    ],
    verbose=True,
    allow_delegation=False
)

def initiate_swarm(origin, dest, weight):
    """
    Orchestrate multi-agent deliberation for optimal routing.
    
    Returns:
        Dictionary containing route analysis and agent recommendations
    """
    
    # Task 1: Carbon Analysis
    carbon_task = Task(
        description=f"""Analyze carbon emissions for shipping {weight} tonnes from {origin} to {dest}.
        
        Compare these modes: standard sea freight, slow-steaming sea freight, and rail.
        Calculate total emissions and carbon tax impact ($100/tonne CO2).
        
        Recommend the GREENEST option and explain the environmental benefits.""",
        expected_output="Detailed carbon analysis with mode comparison and green recommendation",
        agent=carbon_agent
    )
    
    # Task 2: Cost & Speed Analysis
    cost_task = Task(
        description=f"""Analyze cost and delivery time for shipping {weight} tonnes from {origin} to {dest}.
        
        Compare total costs (base + carbon tax) and transit times across all modes.
        Factor in that faster delivery = better cash flow and customer satisfaction.
        
        Recommend the MOST COST-EFFECTIVE option balancing speed and total cost.""",
        expected_output="Cost-speed analysis with business-optimal recommendation",
        agent=cost_agent
    )
    
    # Task 3: Risk Assessment
    risk_task = Task(
        description=f"""Assess risks for shipping from {origin} to {dest}.
        
        Check port congestion levels at both locations.
        Identify potential delays, reliability issues, and alternative routing needs.
        
        Provide a RISK RATING and mitigation strategy.""",
        expected_output="Risk assessment with congestion data and mitigation recommendations",
        agent=risk_agent
    )
    
    # Create the crew
    crew = Crew(
        agents=[carbon_agent, cost_agent, risk_agent],
        tasks=[carbon_task, cost_task, risk_task],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute and return results
    result = crew.kickoff()
    
    # Also return structured data for dashboard
    route_data = LogisticsTools.compare_routes(origin, dest, weight)
    origin_congestion = LogisticsTools.get_port_congestion(origin)
    dest_congestion = LogisticsTools.get_port_congestion(dest)
    
    return {
        'agent_output': str(result),
        'route_comparison': route_data,
        'origin_port_status': origin_congestion,
        'dest_port_status': dest_congestion
    }