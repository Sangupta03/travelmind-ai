from core.llm import call_llm_json
from core.memory import get_user_profile, update_user_profile

CONSTRAINTS_SCHEMA = {
    "type": "object",
    "properties": {
        "budget": {"type": "string"},
        "walking_preference": {"type": "string", "enum": ["low", "medium", "high"]},
        "food_preference": {"type": "string"},
        "pace": {"type": "string", "enum": ["slow", "medium", "fast"]},
        "travel_with_elderly": {"type": "boolean"},
    },
    "required": ["budget", "walking_preference", "food_preference", "pace", "travel_with_elderly"],
}


class UserAgent:
    def extract_constraints(self, user_input: str, username: str) -> dict:
        profile = get_user_profile(username)

        prompt = f"""
        You are an AI that extracts structured travel constraints.

        Past user profile:
        {profile}

        New user input:
        {user_input}
        """

        constraints = call_llm_json(prompt, CONSTRAINTS_SCHEMA)
        if constraints is None:
            constraints = {
                "budget": "unspecified",
                "walking_preference": "medium",
                "food_preference": "unspecified",
                "pace": "medium",
                "travel_with_elderly": False,
            }

        update_user_profile(username, {"last_constraints": constraints})

        return constraints

