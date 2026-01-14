from core.llm import call_llm

class ExperienceAgent:
    def create_plan(self, destination, days, constraints):
        prompt = f"""
        You are an Experience-focused Travel Agent.

        Your goal is to maximize fun, culture, food and sightseeing.

        Destination: {destination}
        Days: {days}
        Constraints: {constraints}

        Suggest:
        - Famous attractions
        - Unique experiences
        - Local food & nightlife

        Output a clear day-wise plan.
        """

        return call_llm(prompt)
