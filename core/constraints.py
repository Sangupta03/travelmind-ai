class BudgetEngine:
    def __init__(self, max_budget):
        self.max_budget = max_budget

    def calculate_total_cost(self, flight_cost, hotel_cost, local_cost, food_cost):
        return flight_cost + hotel_cost + local_cost + food_cost

    def is_within_budget(self, total_cost):
        return total_cost <= self.max_budget
