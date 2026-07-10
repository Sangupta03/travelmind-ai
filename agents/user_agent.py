from core.llm import call_llm_json

CONSTRAINTS_SCHEMA = {
    "type": "object",
    "properties": {
        "budget": {
            "type": "string",
            "description": "The traveler's budget level, e.g. 'low', 'high', 'strict budget'. Use 'unspecified' if not mentioned.",
        },
        "walking_preference": {
            "type": "string",
            "enum": ["low", "medium", "high", "flexible"],
            "description": "How much walking the traveler wants. Use 'flexible' if they say they have no preference or are open to either.",
        },
        "food_preference": {
            "type": "string",
            "description": "Dietary preference, e.g. 'vegetarian', 'no restrictions'. Use 'unspecified' if not mentioned.",
        },
        "pace": {
            "type": "string",
            "enum": ["slow", "medium", "fast", "flexible"],
            "description": "How packed the itinerary should be. Use 'flexible' if the traveler says they don't mind either way.",
        },
        "travel_with_elderly": {"type": "boolean"},
        "interests": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Specific activities or places the traveler wants included, e.g. 'spa', 'church', 'local markets', 'museums'. Empty list if none mentioned.",
        },
    },
    "required": [
        "budget", "walking_preference", "food_preference",
        "pace", "travel_with_elderly", "interests",
    ],
}


class UserAgent:
    def extract_constraints(self, user_input: str, previous_constraints: dict = None) -> dict:
        prompt = f"""
        You are an AI that extracts structured travel constraints.

        Constraints from the traveler's previous trip, if any (use only as
        a hint — the new input below always takes priority):
        {previous_constraints or "None"}

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
                "interests": [],
            }

        return constraints

