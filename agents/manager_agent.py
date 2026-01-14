from agents.user_agent import UserAgent
from agents.budget_agent import BudgetAgent
from agents.comfort_agent import ComfortAgent
from agents.experience_agent import ExperienceAgent
from agents.negotiator_agent import NegotiatorAgent
from core.scoring import score_plan

class ManagerAgent:
    def __init__(self):
        self.user_agent = UserAgent()
        self.budget_agent = BudgetAgent()
        self.comfort_agent = ComfortAgent()
        self.experience_agent = ExperienceAgent()
        self.negotiator_agent = NegotiatorAgent()

    def build_travel_plan(self, user_input, destination, days):
        print("\n🔍 Extracting user constraints...")
        constraints = self.user_agent.extract_constraints(user_input)

        print("\n💰 Budget Agent generating plan...")
        budget_plan = self.budget_agent.create_plan(destination, days, constraints)

        print("\n🛋️ Comfort Agent generating plan...")
        comfort_plan = self.comfort_agent.create_plan(destination, days, constraints)

        print("\n🎉 Experience Agent generating plan...")
        experience_plan = self.experience_agent.create_plan(destination, days, constraints)

        print("\n⚖️ Scoring candidate plans...")
        budget_score = score_plan(budget_plan, constraints)
        comfort_score = score_plan(comfort_plan, constraints)
        experience_score = score_plan(experience_plan, constraints)

        print(f"Budget Plan Score: {budget_score}")
        print(f"Comfort Plan Score: {comfort_score}")
        print(f"Experience Plan Score: {experience_score}")

        print("\n🤝 Negotiator Agent creating optimized plan...")
        final_plan = self.negotiator_agent.negotiate(
            budget_plan, comfort_plan, experience_plan, constraints
        )

        return {
            "constraints": constraints,
            "budget_plan": budget_plan,
            "comfort_plan": comfort_plan,
            "experience_plan": experience_plan,
            "final_plan": final_plan,
            "scores": {
                "budget": budget_score,
                "comfort": comfort_score,
                "experience": experience_score
            }
        }

