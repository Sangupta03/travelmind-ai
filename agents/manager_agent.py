from agents.user_agent import UserAgent
from agents.budget_agent import BudgetAgent
from agents.comfort_agent import ComfortAgent
from agents.experience_agent import ExperienceAgent
from agents.negotiator_agent import NegotiatorAgent

from core.maps_optimizer import MapsOptimizer
from core.walking_estimator import WalkingEstimator
from core.daily_time_engine import DailyTimeEngine
from core.transport_engine import TransportEngine

from tools.attractions_tool import AttractionsTool
from tools.route_links import RouteLinkGenerator
from tools.maps_tool import MapsTool

from core.constraints import BudgetEngine
from core.validator import ConstraintValidator
import json

class ManagerAgent:

    def __init__(self):
        self.user_agent = UserAgent()
        self.budget_agent = BudgetAgent()
        self.comfort_agent = ComfortAgent()
        self.experience_agent = ExperienceAgent()
        self.negotiator_agent = NegotiatorAgent()

        # Maps Intelligence
        self.maps_optimizer = MapsOptimizer()
        self.walking_estimator = WalkingEstimator()
        self.attractions_tool = AttractionsTool()
        self.daily_time_engine = DailyTimeEngine(max_hours_per_day=8)
        self.transport_engine = TransportEngine(
            walk_max_meters=800,
            walk_max_minutes=12
        )
        self.route_links = RouteLinkGenerator()
        self.maps_tool = MapsTool()

        # Hard Constraints
        self.budget_engine = BudgetEngine(max_budget=70000)
        self.validator = ConstraintValidator()

    # =========================================================

    def build_travel_plan(self, username, user_input, destination, days):

        print("\n🔍 Extracting user constraints with memory...")
        #constraints = self.user_agent.extract_constraints(user_input, username)
        constraints_raw = self.user_agent.extract_constraints(user_input, username)

        # convert to dict if string
        if isinstance(constraints_raw, str):
            try:
                constraints = json.loads(constraints_raw)
            except:
                constraints = {"raw": constraints_raw}
        else:
            constraints = constraints_raw

        # -----------------------------
        # AGENT PLANS
        # -----------------------------

        print("\n💰 Budget Agent generating plan...")
        budget_result = self.budget_agent.create_plan(destination, days, constraints)
        budget_plan = budget_result["plan"]
        hotel = budget_result["hotel"]

        print("\n🛋️ Comfort Agent generating plan...")
        comfort_plan = self.comfort_agent.create_plan(destination, days, constraints)

        print("\n🎉 Experience Agent generating plan...")
        experience_plan = self.experience_agent.create_plan(destination, days, constraints)

        print("\n🤝 Negotiator Agent creating optimized plan...")
        final_plan = self.negotiator_agent.negotiate(
            budget_plan,
            comfort_plan,
            experience_plan,
            constraints
        )

        if not final_plan:
            final_plan = "⚠️ Negotiator returned empty plan — fallback used."

        # -----------------------------
        # HARD CONSTRAINT ENGINE
        # -----------------------------

        flight_cost = 6000
        hotel_cost = 2500 * days
        local_cost = 3000
        food_cost = 4000

        total_cost = self.budget_engine.calculate_total_cost(
            flight_cost,
            hotel_cost,
            local_cost,
            food_cost
        )

        if not self.budget_engine.is_within_budget(total_cost):
            final_plan += "\n\n⚠️ WARNING: Plan exceeds budget."

        if not self.validator.validate(constraints, final_plan):
            final_plan += "\n\n⚠️ WARNING: Plan violates constraints."

        # -----------------------------
        # MAPS INTELLIGENCE
        # -----------------------------

        print("\n🗺️ Optimizing route with Google Maps...")

        attractions = self.attractions_tool.get_attractions(destination)

        hotel_name = hotel.get("name", destination)
        start_point = f"{hotel_name}, {destination}"

        ordered_places = self.maps_optimizer.order_by_nearest(
            start_point,
            attractions[:6]
        )

        # -----------------------------
        # DAILY TIME ENGINE
        # -----------------------------

        print("\n⏱️ Applying daily time budgeting...")

        daily_plan = self.daily_time_engine.build_daily_plan(
            start_point=start_point,
            places=ordered_places,
            visit_minutes=60
        )

        # -----------------------------
        # TEXT BLOCK — MAP INSIGHTS
        # -----------------------------

        maps_text = f"""

========== MAPS INTELLIGENCE ==========

🏨 Hotel: {hotel_name}

Nearby Attractions:
{attractions}

Optimized Order:
{ordered_places}

=====================================
"""

        final_plan += maps_text

        # -----------------------------
        # TEXT BLOCK — DAILY PLAN
        # -----------------------------

        daily_text = "\n========== DAILY TIME ITINERARY ==========\n"

        for i, day in enumerate(daily_plan, start=1):
            daily_text += f"\nDay {i}:\n"
            for item in day:
                daily_text += (
                    f"- {item['place']} "
                    f"(Travel {item['travel_time']}, "
                    f"{item['distance']}, "
                    f"Visit {item['visit_time']})\n"
                )

        final_plan += daily_text

        # -----------------------------
        # TRANSPORT LINKS
        # -----------------------------

        print("\n🚕 Generating transport links...")

        transport_rows = []

        for i in range(len(ordered_places) - 1):

            o = ordered_places[i]
            d = ordered_places[i + 1]

            decision = self.transport_engine.decide(o, d)

            mode = "walking" if decision["mode"] == "WALK" else "driving"

            link = self.route_links.generate(o, d, mode)

            transport_rows.append({
                "from": o,
                "to": d,
                "mode": decision["mode"],
                "distance": decision["distance"],
                "time": decision["time"],
                "reason": decision["reason"],
                "link": link
            })

        # -----------------------------
        # RETURN TO HOTEL LEG
        # -----------------------------

        if ordered_places:
            last = ordered_places[-1]

            ret = self.transport_engine.decide(last, start_point)
            ret_mode = "walking" if ret["mode"] == "WALK" else "driving"
            ret_link = self.route_links.generate(last, start_point, ret_mode)

            transport_rows.append({
                "from": last,
                "to": hotel_name,
                "mode": ret["mode"],
                "distance": ret["distance"],
                "time": ret["time"],
                "reason": ret["reason"],
                "link": ret_link
            })

        # -----------------------------
        # FINAL TEXT HEADER
        # -----------------------------

        final_plan = f"\n🏨 Selected Hotel: {hotel_name}\n" + final_plan

        # -----------------------------
        # IMPORTANT — STRUCTURED RETURN
        # -----------------------------

        return {
            "constraints": constraints,
            "estimated_cost": total_cost,
            "final_plan": final_plan,
            "hotel": hotel_name,
            "ordered_places": ordered_places,
            "daily_plan": daily_plan,
            "transport": transport_rows
        }

