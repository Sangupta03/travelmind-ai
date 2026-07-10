"""
Golden test cases for the constraint-extraction eval harness.

Each case is a realistic free-text trip description plus the constraints
we expect Gemini to correctly pull out of it. Add new cases here as you
find real inputs the model gets wrong.
"""

CASES = [
    {
        "name": "budget + vegetarian + elderly",
        "input": "We want a low budget trip, strictly vegetarian food, and we're travelling with my elderly parents so please keep it relaxed.",
        "expect": {
            "food_preference": "vegetarian",
            "travel_with_elderly": True,
            "pace": "slow",
        },
    },
    {
        "name": "low walking preference stated directly",
        "input": "I can't walk long distances, please plan a trip with minimal walking.",
        "expect": {
            "walking_preference": "low",
        },
    },
    {
        "name": "fast paced high energy trip",
        "input": "I want to see as much as possible in a short time, pack the days full, I don't mind walking a lot.",
        "expect": {
            "pace": "fast",
            "walking_preference": "high",
        },
    },
    {
        "name": "no special requirements mentioned",
        "input": "Just a normal relaxing holiday, nothing special needed.",
        "expect": {
            "travel_with_elderly": False,
        },
    },
    {
        "name": "high budget comfort trip",
        "input": "Money is not a concern, we want a comfortable luxury trip with good hotels.",
        "expect": {
            "budget": "high",
        },
    },
]
