import math

class LogisticsTools:
    @staticmethod
    def calculate_carbon(distance, weight, mode):
        # Emission factors (kg CO2 per tonne-km)
        factors = {'sea': 0.015, 'air': 0.50, 'rail': 0.03, 'road': 0.10}
        base_emissions = distance * weight * factors.get(mode, 0.10)
        return round(base_emissions / 1000, 2) # Returns Metric Tonnes CO2

    @staticmethod
    def get_port_congestion(port_name):
        # In a real win, you'd API call here. For the prototype, simulate logic.
        import random
        return random.randint(1, 10) # 1-10 scale of delay