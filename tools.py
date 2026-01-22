import math
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

# Input schemas for tools
class RouteInput(BaseModel):
    origin: str = Field(..., description="Origin port/city")
    destination: str = Field(..., description="Destination port/city")
    weight: float = Field(..., description="Cargo weight in metric tonnes")
    mode: str = Field(..., description="Transport mode: sea, sea_slow, rail, air, road")

class PortInput(BaseModel):
    port_name: str = Field(..., description="Name of the port")

class CompareInput(BaseModel):
    origin: str = Field(..., description="Origin location")
    destination: str = Field(..., description="Destination location")
    weight: float = Field(..., description="Cargo weight in tonnes")

# Distance database (km)
DISTANCES = {
    ('Shanghai', 'Rotterdam'): {'sea': 20000, 'rail': 11000},
    ('Singapore', 'London'): {'sea': 13000, 'rail': 12000},
    ('Mumbai', 'Hamburg'): {'sea': 8500, 'rail': 7000},
    ('Dubai', 'Amsterdam'): {'sea': 6500, 'rail': 5500},
}

# Emission factors (kg CO2 per tonne-km)
EMISSION_FACTORS = {
    'sea': 0.015,
    'sea_slow': 0.011,
    'air': 0.50,
    'rail': 0.03,
    'road': 0.10
}

# Cost per tonne-km (USD)
COST_FACTORS = {
    'sea': 0.05,
    'sea_slow': 0.04,
    'rail': 0.08,
    'air': 1.20,
    'road': 0.15
}

# Transit time (days per 1000km)
TIME_FACTORS = {
    'sea': 4,
    'sea_slow': 6,
    'rail': 2,
    'air': 0.3,
    'road': 1.5
}

class CarbonCalculatorTool(BaseTool):
    name: str = "Carbon Calculator"
    description: str = "Calculate carbon emissions, cost, and transit time for a shipment route"
    args_schema: Type[BaseModel] = RouteInput

    def _run(self, origin: str, destination: str, weight: float, mode: str) -> dict:
        route_key = (origin, destination)
        
        # Get distance
        if route_key in DISTANCES:
            distance = DISTANCES[route_key].get(mode.replace('_slow', ''), 10000)
        else:
            distance = 10000
        
        # Calculate emissions (tonnes CO2)
        emission_factor = EMISSION_FACTORS.get(mode, 0.10)
        total_emissions = (distance * weight * emission_factor) / 1000
        
        # Calculate cost
        cost_factor = COST_FACTORS.get(mode, 0.10)
        base_cost = distance * weight * cost_factor
        
        # Calculate carbon tax ($100/tonne CO2)
        carbon_tax = total_emissions * 100
        total_cost = base_cost + carbon_tax
        
        # Calculate transit time
        time_factor = TIME_FACTORS.get(mode, 2)
        transit_days = (distance / 1000) * time_factor
        
        return {
            'mode': mode,
            'distance_km': distance,
            'emissions_tonnes': round(total_emissions, 2),
            'base_cost_usd': round(base_cost, 2),
            'carbon_tax_usd': round(carbon_tax, 2),
            'total_cost_usd': round(total_cost, 2),
            'transit_days': round(transit_days, 1)
        }

class PortCongestionTool(BaseTool):
    name: str = "Port Congestion Checker"
    description: str = "Get congestion and delay information for a port"
    args_schema: Type[BaseModel] = PortInput

    def _run(self, port_name: str) -> dict:
        import random
        random.seed(hash(port_name) % 100)
        
        congestion_level = random.randint(3, 9)
        delay_days = round(congestion_level * 0.5, 1)
        status = "Low" if congestion_level <= 4 else "Moderate" if congestion_level <= 7 else "High"
        
        return {
            'port': port_name,
            'congestion_level': congestion_level,
            'status': status,
            'estimated_delay_days': delay_days,
            'berth_availability': f"{random.randint(40, 95)}%"
        }

class RouteCompareTool(BaseTool):
    name: str = "Route Comparer"
    description: str = "Compare multiple transport modes for a route"
    args_schema: Type[BaseModel] = CompareInput

    def _run(self, origin: str, destination: str, weight: float) -> list:
        modes = ['sea', 'sea_slow', 'rail']
        results = []
        calc_tool = CarbonCalculatorTool()
        
        for mode in modes:
            result = calc_tool._run(origin, destination, weight, mode)
            results.append(result)
        
        return results

# Helper functions for dashboard (non-tool usage)
class LogisticsTools:
    @staticmethod
    def calculate_carbon(origin: str, destination: str, weight: float, mode: str) -> dict:
        tool = CarbonCalculatorTool()
        return tool._run(origin, destination, weight, mode)
    
    @staticmethod
    def get_port_congestion(port_name: str) -> dict:
        tool = PortCongestionTool()
        return tool._run(port_name)
    
    @staticmethod
    def compare_routes(origin: str, destination: str, weight: float) -> list:
        tool = RouteCompareTool()
        return tool._run(origin, destination, weight)