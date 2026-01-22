from crewai import Agent, Task, Crew, Process
from tools import CarbonCalculatorTool, PortCongestionTool, RouteCompareTool, LogisticsTools

# Initialize tool instances
carbon_calc = CarbonCalculatorTool()
port_check = PortCongestionTool()
route_compare = RouteCompareTool()

# Agent 1: The Green Auditor
carbon_agent = Agent(
    role='Carbon Emission Specialist',
    goal='Minimize CO2 footprint by selecting greener transport modes and carbon-efficient routing.',
    backstory="""You are a radical environmental scientist who prioritizes planetary health. 
    You analyze emissions data, advocate for slow-steaming and rail transport, and calculate 
    the true environmental cost of every logistics decision. Carbon tax is your weapon.""",
    tools=[carbon_calc, route_compare, port_check],
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
    tools=[carbon_calc, route_compare, port_check],
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
    tools=[port_check, route_compare],
    verbose=True,
    allow_delegation=False
)

def calculate_trilemma_score(route, weights={'cost': 0.33, 'carbon': 0.33, 'time': 0.34}):
    """
    Calculate trilemma optimization score for a route.
    Lower is better (normalized penalty score).
    """
    # Normalize each factor (simple linear scaling for demo)
    cost_penalty = route['total_cost_usd'] / 100000  # Normalize to 0-1 range
    carbon_penalty = route['emissions_tonnes'] / 100  # Normalize to 0-1 range
    time_penalty = route['transit_days'] / 100  # Normalize to 0-1 range
    
    # Weighted trilemma score
    score = (
        weights['cost'] * cost_penalty +
        weights['carbon'] * carbon_penalty +
        weights['time'] * time_penalty
    )
    
    return round(score, 4)

def select_optimal_route(route_data, origin_congestion, dest_congestion, weights=None):
    """
    AI-driven route selection based on trilemma optimization.
    Returns the selected route with reasoning.
    """
    if weights is None:
        weights = {'cost': 0.33, 'carbon': 0.33, 'time': 0.34}
    
    # Calculate trilemma scores
    for route in route_data:
        route['trilemma_score'] = calculate_trilemma_score(route, weights)
    
    # Select optimal (lowest score)
    optimal = min(route_data, key=lambda x: x['trilemma_score'])
    
    # Generate reasoning bullets
    reasons = []
    
    # Carbon tax analysis
    carbon_tax_pct = (optimal['carbon_tax_usd'] / optimal['total_cost_usd']) * 100
    if carbon_tax_pct > 15:
        reasons.append(f"⚠️ Carbon tax represents {carbon_tax_pct:.1f}% of total cost - green routing critical")
    
    # Congestion risk
    avg_congestion = (origin_congestion['congestion_level'] + dest_congestion['congestion_level']) / 2
    if avg_congestion > 6:
        reasons.append(f"🚨 High port congestion ({avg_congestion:.1f}/10) - reliability prioritized")
    elif avg_congestion < 4:
        reasons.append(f"✅ Low congestion risk ({avg_congestion:.1f}/10) - stable route conditions")
    
    # Emission efficiency
    emissions_sorted = sorted(route_data, key=lambda x: x['emissions_tonnes'])
    if optimal == emissions_sorted[0]:
        emission_reduction = ((route_data[0]['emissions_tonnes'] - optimal['emissions_tonnes']) / route_data[0]['emissions_tonnes']) * 100
        if emission_reduction > 5:
            reasons.append(f"🌱 Achieves {emission_reduction:.1f}% emission reduction vs baseline")
    
    # Cost efficiency
    if optimal['total_cost_usd'] == min(r['total_cost_usd'] for r in route_data):
        reasons.append(f"💰 Most cost-effective option at ${optimal['total_cost_usd']:,.0f}")
    
    # Time factor
    if optimal['transit_days'] < 50:
        reasons.append(f"⚡ Fast delivery ({optimal['transit_days']:.1f} days) maintains supply chain velocity")
    
    # Trilemma improvement
    baseline_score = route_data[0]['trilemma_score']
    if optimal['trilemma_score'] < baseline_score:
        improvement_pct = ((baseline_score - optimal['trilemma_score']) / baseline_score) * 100
        reasons.append(f"📊 Net trilemma score improved by {improvement_pct:.1f}%")
    
    # Ensure we have at least 2-3 bullets
    if len(reasons) < 2:
        reasons.append(f"🎯 Balanced optimization across cost, carbon, and time constraints")
    
    return {
        'selected_mode': optimal['mode'],
        'selected_route': optimal,
        'trilemma_score': optimal['trilemma_score'],
        'reasoning': reasons[:3],  # Top 3 reasons
        'all_scores': {r['mode']: r['trilemma_score'] for r in route_data}
    }

def initiate_swarm(origin, dest, weight, trilemma_weights=None):
    """
    Orchestrate multi-agent deliberation for optimal routing.
    
    Returns:
        Dictionary containing route analysis and agent recommendations
    """
    
    # Task 1: Carbon Analysis
    carbon_task = Task(
        description=f"""Analyze carbon emissions for shipping {weight} tonnes from {origin} to {dest}.
        
        Use the Route Comparer tool to compare these modes: standard sea freight, slow-steaming sea freight, and rail.
        Calculate total emissions and carbon tax impact ($100/tonne CO2).
        
        Recommend the GREENEST option and explain the environmental benefits.""",
        expected_output="Detailed carbon analysis with mode comparison and green recommendation",
        agent=carbon_agent
    )
    
    # Task 2: Cost & Speed Analysis
    cost_task = Task(
        description=f"""Analyze cost and delivery time for shipping {weight} tonnes from {origin} to {dest}.
        
        Use the Route Comparer tool to compare total costs (base + carbon tax) and transit times across all modes.
        Factor in that faster delivery = better cash flow and customer satisfaction.
        
        Recommend the MOST COST-EFFECTIVE option balancing speed and total cost.""",
        expected_output="Cost-speed analysis with business-optimal recommendation",
        agent=cost_agent
    )
    
    # Task 3: Risk Assessment
    risk_task = Task(
        description=f"""Assess risks for shipping from {origin} to {dest}.
        
        Use the Port Congestion Checker to check congestion levels at {origin} and {dest}.
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
    
    # AI-driven route selection
    optimal_decision = select_optimal_route(route_data, origin_congestion, dest_congestion, trilemma_weights)
    
    return {
        'agent_output': str(result),
        'route_comparison': route_data,
        'origin_port_status': origin_congestion,
        'dest_port_status': dest_congestion,
        'optimal_decision': optimal_decision
    }