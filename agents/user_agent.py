from core.llm import call_llm
from core.memory import get_user_profile, update_user_profile

class UserAgent:
    def extract_constraints(self, user_input: str, username: str):
        profile = get_user_profile(username)

        prompt = f"""
        You are an AI that extracts structured travel constraints.

        Past user profile:
        {profile}

        New user input:
        {user_input}

        Return JSON with fields:
        - budget
        - walking_preference (low/medium/high)
        - food_preference
        - pace (slow/medium/fast)
        - travel_with_elderly (true/false)
        """

        response = call_llm(prompt)

        # Update memory
        update_user_profile(username, {"last_constraints": response})

        return response

