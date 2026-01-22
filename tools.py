import math
from crewai_tools import tool

class LogisticsTools:
    # Distance database (km) - expandable
    DISTANCES = {
        ('Shanghai', 'Rotterdam'): {'sea': 20000, 'rail': 11000},
        ('Singapore', 'London'): {'sea': 13000, 'rail': 12000},
        ('Mumbai', 'Hamburg'): {'sea': 8500, 'rail': 7000},
        ('Dubai', 'Amsterdam'): {'sea': 6500, 'rail': 5500},
    }
    
    # Emission factors (kg CO2 per tonne-km)
    EMISSION_FACTORS = {
        'sea': 0.015,
        'sea_slow': 0.011,  # Slow steaming reduces emissions
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

    @staticmethod
    @tool("Calculate carbon emissions for a route")
    def calculate_carbon(origin: str, destination: str, weight: float, mode: str) -> dict:
        """
        Calculate carbon emissions for a shipment route.
        
        Args:
            origin: Origin port/city
            destination: Destination port/city
            weight: Cargo weight in metric tonnes
            mode: Transport mode (sea, sea_slow, rail, air, road)
        
        Returns:
            Dictionary with emissions, cost, and time data
        """
        route_key = (origin, destination)
        
        # Get distance
        if route_key in LogisticsTools.DISTANCES:
            distance = LogisticsTools.DISTANCES[route_key].get(mode.replace('_slow', ''), 10000)
        else:
            distance = 10000  # Default fallback
        
        # Calculate emissions (tonnes CO2)
        emission_factor = LogisticsTools.EMISSION_FACTORS.get(mode, 0.10)
        total_emissions = (distance * weight * emission_factor) / 1000
        
        # Calculate cost
        cost_factor = LogisticsTools.COST_FACTORS.get(mode, 0.10)
        base_cost = distance * weight * cost_factor
        
        # Calculate carbon tax ($100/tonne CO2)
        carbon_tax = total_emissions * 100
        total_cost = base_cost + carbon_tax
        
        # Calculate transit time
        time_factor = LogisticsTools.TIME_FACTORS.get(mode, 2)
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

    @staticmethod
    @tool("Get port congestion level")
    def get_port_congestion(port_name: str) -> dict:
        """
        Get congestion and delay information for a port.
        
        Args:
            port_name: Name of the port
            
        Returns:
            Dictionary with congestion data
        """
        import random
        random.seed(hash(port_name) % 100)  # Consistent results per port
        
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

    @staticmethod
    @tool("Compare multiple route options")
    def compare_routes(origin: str, destination: str, weight: float) -> list:
        """
        Compare multiple transport modes for a route.
        
        Args:
            origin: Origin location
            destination: Destination location
            weight: Cargo weight in tonnes
            
        Returns:
            List of route comparisons
        """
        modes = ['sea', 'sea_slow', 'rail']
        results = []
        
        for mode in modes:
            result = LogisticsTools.calculate_carbon(origin, destination, weight, mode)
            results.append(result)
        
        return results