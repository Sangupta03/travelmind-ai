from core.llm import call_llm

class UserAgent:
    def extract_constraints(self, user_input: str):
        prompt = f"""
        You are an AI that extracts structured travel constraints.

        User input:
        {user_input}

        Return JSON with fields:
        - budget
        - walking_preference (low/medium/high)
        - food_preference
        - pace (slow/medium/fast)
        - travel_with_elderly (true/false)

        Only return JSON.
        """

        response = call_llm(prompt)
        return response
