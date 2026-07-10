"""
agents/manager_agent.py — Updated with PARALLEL agent execution
Replace your existing agents/manager_agent.py with this file.

Key change: Budget, Comfort, and Experience agents now run
simultaneously using ThreadPoolExecutor instead of sequentially.
This is the difference between a toy system and a real one.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import json
import logging
import time

logger = logging.getLogger(__name__)

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

    def _run_budget(self, destination, days, constraints, departure_date=None, origin="Delhi", selected_hotel=None):
        logger.info("[parallel] BudgetAgent starting...")
        result = self.budget_agent.create_plan(destination, days, constraints, departure_date, origin, selected_hotel)
        logger.info("[parallel] BudgetAgent done.")
        return result

    def _run_comfort(self, destination, days, constraints):
        logger.info("[parallel] ComfortAgent starting...")
        result = self.comfort_agent.create_plan(destination, days, constraints)
        logger.info("[parallel] ComfortAgent done.")
        return result

    def _run_experience(self, destination, days, constraints):
        logger.info("[parallel] ExperienceAgent starting...")
        result = self.experience_agent.create_plan(destination, days, constraints)
        logger.info("[parallel] ExperienceAgent done.")
        return result

    # =========================================================
    # MAIN — build_travel_plan
    # =========================================================

    def build_travel_plan(self, username, user_input, destination, days, departure_date=None, origin="Delhi", toggles=None, selected_hotel=None):

        # --------------------------------------------------
        # 1. Extract user constraints (sequential — needed
        #    before agents can start)
        # --------------------------------------------------
        logger.info("Extracting user constraints...")
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

        # Quick-toggle checkboxes are deterministic — they override
        # whatever (or nothing) the LLM inferred from free text.
        if toggles:
            if toggles.get("low_walking"):
                constraints["walking_preference"] = "low"
            if toggles.get("budget_strict"):
                constraints["budget"] = "strict budget"
            if toggles.get("elderly"):
                constraints["travel_with_elderly"] = True
            if toggles.get("vegetarian"):
                constraints["food_preference"] = "vegetarian"
            if toggles.get("family"):
                constraints["family_trip"] = True

        # --------------------------------------------------
        # 2. Run Budget, Comfort, Experience IN PARALLEL
        #    This is the core improvement over the old version.
        #    All three LLM calls happen simultaneously.
        # --------------------------------------------------
        logger.info("Launching Budget, Comfort, Experience agents in parallel...")
        t_start = time.time()

        budget_result  = None
        comfort_plan   = None
        experience_plan = None

        # Map each future to its agent name for error reporting
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_budget     = executor.submit(self._run_budget,     destination, days, constraints, departure_date, origin, selected_hotel)
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
                    logger.info("%s completed.", name)
                except Exception as exc:
                    logger.error("%s failed: %s", name, exc)
                    # Provide safe fallbacks so the pipeline continues
                    if name == "BudgetAgent":
                        budget_result = {"plan": "Budget plan unavailable.", "hotel": {"name": destination}}
                    elif name == "ComfortAgent":
                        comfort_plan = "Comfort plan unavailable."
                    elif name == "ExperienceAgent":
                        experience_plan = "Experience plan unavailable."

        elapsed = round(time.time() - t_start, 1)
        logger.info("All 3 agents finished in %ss (parallel)", elapsed)

        # Extract from budget result
        budget_plan = budget_result.get("plan", "") if budget_result else ""
        hotel       = budget_result.get("hotel", {"name": destination}) if budget_result else {"name": destination}
        flights     = budget_result.get("flights", []) if budget_result else []

        # --------------------------------------------------
        # 3. Negotiator merges the three plans (sequential —
        #    depends on all three outputs above)
        # --------------------------------------------------
        logger.info("NegotiatorAgent merging plans...")
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
        if flights and flights[0].get("price_value"):
            flight_cost = round(flights[0]["price_value"])

        hotel_cost = 2500 * days
        hotel_price_raw = hotel.get("price") if isinstance(hotel, dict) else None
        if hotel_price_raw:
            try:
                per_night = float(str(hotel_price_raw).replace("₹", "").replace(",", "").strip())
                hotel_cost = round(per_night * days)
            except ValueError:
                pass

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
        logger.info("Optimizing route with Google Maps...")
        places_needed = min(max(days * 3, 6), 20)
        attractions = self.attractions_tool.get_attractions(destination, limit=places_needed)
        hotel_name  = hotel.get("name", destination)
        start_point = f"{hotel_name}, {destination}"

        ordered_places = self.maps_optimizer.order_by_nearest(
            start_point, attractions
        )

        # --------------------------------------------------
        # 6. Daily time engine
        # --------------------------------------------------
        logger.info("Building daily schedule...")
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
        logger.info("Generating transport links...")
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
        # 7b. Calendar dates per day (only if a departure date was given)
        # --------------------------------------------------
        day_dates = []
        if departure_date:
            try:
                start = datetime.strptime(departure_date, "%Y-%m-%d")
                day_dates = [(start + timedelta(days=i)).strftime("%d %b %Y") for i in range(len(daily_plan))]
            except ValueError:
                day_dates = []

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
            "departure_date": departure_date,
            "day_dates":      day_dates,
            "flights":        flights,

            # Metadata for UI / resume talking point
            "agent_execution": "parallel",
            "parallel_time_seconds": elapsed,
        }