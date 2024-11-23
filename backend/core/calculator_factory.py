from .stats_calculator import StatsCalculator

class CalculatorFactory:
    @staticmethod
    def get_calculator(calculator_type):
        if calculator_type == "stats":
            return StatsCalculator()
        # Add more calculator types here as needed
        else:
            raise ValueError(f"Unknown calculator type: {calculator_type}")