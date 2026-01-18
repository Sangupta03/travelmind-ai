from core.llm import call_llm

class NegotiatorAgent:
    def negotiate(self, budget_plan, comfort_plan, experience_plan, constraints):

        prompt = f"""
        You are a Travel Negotiator AI.

        Budget Plan:
        {budget_plan}

        Comfort Plan:
        {comfort_plan}

        Experience Plan:
        {experience_plan}

        User Constraints:
        {constraints}

        Merge the best parts of all three plans into one optimal travel plan.
        """

        final_plan = call_llm(prompt)
        return final_plan

