from core.llm import call_llm

class NegotiatorAgent:
    def negotiate(self, budget_plan, comfort_plan, experience_plan, constraints):
        prompt = f"""
        You are a senior AI Travel Negotiator.

        Your job is to combine the best parts of these three plans
        into one optimal itinerary that respects user constraints.

        User Constraints:
        {constraints}

        Budget Plan:
        {budget_plan}

        Comfort Plan:
        {comfort_plan}

        Experience Plan:
        {experience_plan}

        Produce:
        1. Final optimized day-wise itinerary
        2. Clear reasoning explaining why this plan was chosen
        """

        return call_llm(prompt)
