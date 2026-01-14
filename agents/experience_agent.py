from core.llm import call_llm
from tools.places_tool import search_places

class ExperienceAgent:
    def create_plan(self, destination, days, constraints):
        places = search_places(destination)

        prompt = f"""
        You are an Experience Travel Agent.

        Popular Places:
        {places}

        Destination: {destination}
        Days: {days}
        Constraints: {constraints}

        Create an exciting sightseeing plan.
        """

        return call_llm(prompt)

