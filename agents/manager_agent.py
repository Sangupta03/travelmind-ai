from agents.user_agent import UserAgent
from agents.budget_agent import BudgetAgent
from agents.comfort_agent import ComfortAgent
from agents.experience_agent import ExperienceAgent
from agents.negotiator_agent import NegotiatorAgent

from core.constraints import BudgetEngine
from core.optimizer import TimeOptimizer, WalkingOptimizer, DistanceOptimizer
from core.validator import ConstraintValidator


class ManagerAgent:
    def __init__(self):
        self.user_agent = UserAgent()
        self.budget_agent = BudgetAgent()
        self.comfort_agent = ComfortAgent()
        self.experience_agent = ExperienceAgent()
        self.negotiator_agent = NegotiatorAgent()

        # Hard constraint engines
        self.budget_engine = BudgetEngine(max_budget=70000)
        self.validator = ConstraintValidator()

    def build_travel_plan(self, username, user_input, destination, days):
        print("\n🔍 Extracting user constraints with memory...")
        constraints = self.user_agent.extract_constraints(user_input, username)

        print("\n💰 Budget Agent generating plan...")
        budget_plan = self.budget_agent.create_plan(destination, days, constraints)

        print("\n🛋️ Comfort Agent generating plan...")
        comfort_plan = self.comfort_agent.create_plan(destination, days, constraints)

        print("\n🎉 Experience Agent generating plan...")
        experience_plan = self.experience_agent.create_plan(destination, days, constraints)

        print("\n🤝 Negotiator Agent creating optimized plan...")
        final_plan = self.negotiator_agent.negotiate(
            budget_plan, comfort_plan, experience_plan, constraints
        )

        # -----------------------------
        # HARD CONSTRAINT ENGINE
        # -----------------------------

        # Example cost model (later replaced by real APIs)
        flight_cost = 6000
        hotel_cost = 2500 * days
        local_cost = 3000
        food_cost = 4000

        total_cost = self.budget_engine.calculate_total_cost(
            flight_cost, hotel_cost, local_cost, food_cost
        )

        if not self.budget_engine.is_within_budget(total_cost):
            final_plan += "\n\n⚠️ WARNING: This plan exceeds your budget limit."

        # Validate constraints
        if not self.validator.validate(constraints, final_plan):
            final_plan += "\n\n⚠️ WARNING: This plan violates your walking/food constraints."

        return {
            "constraints": constraints,
            "estimated_cost": total_cost,
            "final_plan": final_plan
        }


