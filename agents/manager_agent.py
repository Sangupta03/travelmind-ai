"""
agents/manager_agent.py — Updated with PARALLEL agent execution
Replace your existing agents/manager_agent.py with this file.

Key change: Budget, Comfort, and Experience agents now run
simultaneously using ThreadPoolExecutor instead of sequentially.
This is the difference between a toy system and a real one.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import time

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


class ManagerAgent:

    def __init__(self):
        self.user_agent       = UserAgent()
        self.budget_agent     = BudgetAgent()
        self.comfort_agent    = ComfortAgent()
        self.experience_agent = ExperienceAgent()
        self.negotiator_agent = NegotiatorAgent()

        self.maps_optimizer   = MapsOptimizer()
        self.walking_estimator = WalkingEstimator()
        self.attractions_tool = AttractionsTool()
        self.daily_time_engine = DailyTimeEngine(max_hours_per_day=8)
        self.transport_engine  = TransportEngine(
            walk_max_meters=800,
            walk_max_minutes=12
        )
        self.route_links = RouteLinkGenerator()
        self.maps_tool   = MapsTool()

        self.budget_engine = BudgetEngine(max_budget=70000)
        self.validator     = ConstraintValidator()

    # =========================================================
    # PRIVATE — run one agent, return (name, result)
    # =========================================================

    def _run_budget(self, destination, days, constraints):
        print("  [parallel] BudgetAgent starting...")
        result = self.budget_agent.create_plan(destination, days, constraints)
        print("  [parallel] BudgetAgent done.")
        return result

    def _run_comfort(self, destination, days, constraints):
        print("  [parallel] ComfortAgent starting...")
        result = self.comfort_agent.create_plan(destination, days, constraints)
        print("  [parallel] ComfortAgent done.")
        return result

    def _run_experience(self, destination, days, constraints):
        print("  [parallel] ExperienceAgent starting...")
        result = self.experience_agent.create_plan(destination, days, constraints)
        print("  [parallel] ExperienceAgent done.")
        return result

    # =========================================================
    # MAIN — build_travel_plan
    # =========================================================

    def build_travel_plan(self, username, user_input, destination, days):

        # --------------------------------------------------
        # 1. Extract user constraints (sequential — needed
        #    before agents can start)
        # --------------------------------------------------
        print("\nExtracting user constraints...")
        constraints_raw = self.user_agent.extract_constraints(user_input, username)

        if isinstance(constraints_raw, str):
            cleaned = constraints_raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.strip("`")
                if cleaned.lower().startswith("json"):
                    cleaned = cleaned[4:]
                cleaned = cleaned.strip()
            try:
                constraints = json.loads(cleaned)
            except Exception:
                constraints = {"raw": constraints_raw}
        else:
            constraints = constraints_raw

        # --------------------------------------------------
        # 2. Run Budget, Comfort, Experience IN PARALLEL
        #    This is the core improvement over the old version.
        #    All three LLM calls happen simultaneously.
        # --------------------------------------------------
        print("\nLaunching Budget, Comfort, Experience agents in parallel...")
        t_start = time.time()

        budget_result  = None
        comfort_plan   = None
        experience_plan = None

        # Map each future to its agent name for error reporting
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_budget     = executor.submit(self._run_budget,     destination, days, constraints)
            future_comfort    = executor.submit(self._run_comfort,    destination, days, constraints)
            future_experience = executor.submit(self._run_experience, destination, days, constraints)

            futures = {
                future_budget:     "BudgetAgent",
                future_comfort:    "ComfortAgent",
                future_experience: "ExperienceAgent",
            }

            for future in as_completed(futures):
                name = futures[future]
                try:
                    result = future.result()
                    if name == "BudgetAgent":
                        budget_result = result
                    elif name == "ComfortAgent":
                        comfort_plan = result
                    elif name == "ExperienceAgent":
                        experience_plan = result
                    print(f"  {name} completed.")
                except Exception as exc:
                    print(f"  {name} failed: {exc}")
                    # Provide safe fallbacks so the pipeline continues
                    if name == "BudgetAgent":
                        budget_result = {"plan": "Budget plan unavailable.", "hotel": {"name": destination}}
                    elif name == "ComfortAgent":
                        comfort_plan = "Comfort plan unavailable."
                    elif name == "ExperienceAgent":
                        experience_plan = "Experience plan unavailable."

        elapsed = round(time.time() - t_start, 1)
        print(f"\nAll 3 agents finished in {elapsed}s (parallel)")

        # Extract from budget result
        budget_plan = budget_result.get("plan", "") if budget_result else ""
        hotel       = budget_result.get("hotel", {"name": destination}) if budget_result else {"name": destination}

        # --------------------------------------------------
        # 3. Negotiator merges the three plans (sequential —
        #    depends on all three outputs above)
        # --------------------------------------------------
        print("\nNegotiatorAgent merging plans...")
        final_plan = self.negotiator_agent.negotiate(
            budget_plan,
            comfort_plan,
            experience_plan,
            constraints
        )
        if not final_plan:
            final_plan = "⚠️ Negotiator returned empty plan."

        # --------------------------------------------------
        # 4. Hard constraint engine
        # --------------------------------------------------
        flight_cost = 6000
        hotel_cost  = 2500 * days
        local_cost  = 3000
        food_cost   = 4000

        total_cost = self.budget_engine.calculate_total_cost(
            flight_cost, hotel_cost, local_cost, food_cost
        )

        if not self.budget_engine.is_within_budget(total_cost):
            final_plan += "\n\n⚠️ WARNING: Plan exceeds budget."

        if not self.validator.validate(constraints, final_plan):
            final_plan += "\n\n⚠️ WARNING: Plan violates constraints."

        # --------------------------------------------------
        # 5. Maps intelligence
        # --------------------------------------------------
        print("\nOptimizing route with Google Maps...")
        attractions = self.attractions_tool.get_attractions(destination)
        hotel_name  = hotel.get("name", destination)
        start_point = f"{hotel_name}, {destination}"

        places_needed = max(days * 3, 6)
        ordered_places = self.maps_optimizer.order_by_nearest(
            start_point, attractions[:places_needed]
        )

        # --------------------------------------------------
        # 6. Daily time engine
        # --------------------------------------------------
        print("\nBuilding daily schedule...")
        daily_plan = self.daily_time_engine.build_daily_plan(
            start_point=start_point,
            places=ordered_places,
            num_days=days,
            visit_minutes=60
        )

        # --------------------------------------------------
        # 7. Transport decisions (walk vs cab per leg)
        #    Each day starts and ends at the hotel.
        # --------------------------------------------------
        print("\nGenerating transport links...")
        transport_rows = []

        for day_index, day_places in enumerate(daily_plan, start=1):
            route = [start_point] + [item["place"] for item in day_places] + [start_point]

            for i in range(len(route) - 1):
                o = route[i]
                d = route[i + 1]
                if o == d:
                    continue
                decision = self.transport_engine.decide(o, d)
                mode     = "walking" if decision["mode"] == "WALK" else "driving"
                link     = self.route_links.generate(o, d, mode)
                transport_rows.append({
                    "day":      day_index,
                    "from":     hotel_name if o == start_point else o,
                    "to":       hotel_name if d == start_point else d,
                    "mode":     decision["mode"],
                    "distance": decision["distance"],
                    "time":     decision["time"],
                    "reason":   decision["reason"],
                    "link":     link
                })

        cost_breakdown = {
            "flight":          flight_cost,
            "hotel":           hotel_cost,
            "local_transport": local_cost,
            "food":            food_cost
        }

        final_plan = f"\n🏨 Selected Hotel: {hotel_name}\n" + final_plan

        # --------------------------------------------------
        # 8. Structured return
        # --------------------------------------------------
        return {
            "destination":    destination,
            "days_count":     days,
            "hotel":          hotel_name,
            "constraints":    constraints,
            "estimated_cost": total_cost,
            "cost_breakdown": cost_breakdown,
            "attractions":    ordered_places,
            "daily_plan":     daily_plan,
            "transport":      transport_rows,
            "ai_reasoning":   final_plan,

            # Metadata for UI / resume talking point
            "agent_execution": "parallel",
            "parallel_time_seconds": elapsed,
        }