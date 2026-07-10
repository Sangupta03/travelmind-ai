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
            "enum": ["low", "medium", "high", "flexible", "unspecified"],
            "description": "How much walking the traveler wants. Use 'flexible' ONLY if they explicitly say they have no preference or are open to either. Use 'unspecified' if walking wasn't mentioned at all — do not guess.",
        },
        "food_preference": {
            "type": "string",
            "description": "Dietary preference, e.g. 'vegetarian', 'no restrictions'. Use 'unspecified' if not mentioned.",
        },
        "pace": {
            "type": "string",
            "enum": ["slow", "medium", "fast", "flexible", "unspecified"],
            "description": "How packed the itinerary should be. Use 'flexible' ONLY if the traveler explicitly says they don't mind either way. Use 'unspecified' if pace wasn't mentioned at all — do not guess.",
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

