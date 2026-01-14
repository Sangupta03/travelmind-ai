from core.llm import call_llm

class BudgetAgent:
    def create_plan(self, destination, days, constraints):
        prompt = f"""
        You are a Budget Travel Agent.

        Your goal is to minimize cost while respecting user constraints.

        Destination: {destination}
        Days: {days}
        Constraints: {constraints}

        Suggest:
        - Affordable flights
        - Budget hotels
        - Low-cost activities

        Output a clear day-wise plan.
        """

        return call_llm(prompt)
