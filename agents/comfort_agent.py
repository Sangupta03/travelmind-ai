from core.llm import call_llm

class ComfortAgent:
    def create_plan(self, destination, days, constraints):
        prompt = f"""
        You are a Comfort-focused Travel Agent.

        Your goal is to minimize walking and maximize convenience.

        Destination: {destination}
        Days: {days}
        Constraints: {constraints}

        Suggest:
        - Comfortable hotels
        - Easy transportation
        - Relaxed sightseeing

        Output a clear day-wise plan.
        """

        return call_llm(prompt)
