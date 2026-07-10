"""
server.py — TravelMind AI
FastAPI server: JWT auth + SQLite + parallel agents
Run: uvicorn server:app --reload
"""

import json
import logging

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import init_db, get_db, User, Trip
from auth import hash_password, verify_password, create_access_token, get_current_user
from agents.manager_agent import ManagerAgent
from core.constraints import DEFAULT_MAX_BUDGET
from core.preferences import format_preferences
from core.markdown_render import render_ai_reasoning
from tools.hotel_tool import HotelSearch

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="TravelMind AI")
agent = ManagerAgent()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def startup():
    init_db()
    logger.info("Database ready: travelmind.db")


# ── HELPERS ───────────────────────────────────────────────────

def base_ctx(request: Request, user: dict, extra: dict = None) -> dict:
    """
    Build the base template context that every page needs.
    Includes username so the sidebar always renders correctly.
    """
    ctx = {
        "request":  request,
        "username": user.get("name", "Traveller") if user else "Traveller",
    }
    if extra:
        ctx.update(extra)
    return ctx


def build_insights(trip) -> list:
    """Derive AI Insights cards from this trip's actual data."""
    transport = trip.transport
    daily_plan = trip.daily_plan
    constraints = trip.constraints

    walk_count = sum(1 for leg in transport if leg.get("mode") == "WALK")
    cab_count  = sum(1 for leg in transport if leg.get("mode") == "CAB")

    total_km = 0.0
    for leg in transport:
        try:
            total_km += float(str(leg.get("distance", "")).lower().replace("km", "").strip())
        except ValueError:
            pass

    num_days = len(daily_plan) or trip.days_count
    avg_per_day = round(len(trip.attractions) / num_days, 1) if num_days else 0

    budget_pct = round((trip.estimated_cost / DEFAULT_MAX_BUDGET) * 100) if trip.estimated_cost else 0

    applied_constraints = [
        f"{label}: {value}"
        for label, value in format_preferences(constraints).items()
    ]

    return [
        {
            "title": "Route Optimized",
            "text": f"Nearest-neighbor ordering covered {round(total_km, 1)} km across "
                    f"{len(transport)} legs, minimizing total travel time between attractions."
        },
        {
            "title": "Central Hotel Selected",
            "text": f"{trip.hotel} was chosen in {trip.destination} to keep cab distances "
                    f"short while staying within the ₹{DEFAULT_MAX_BUDGET:,} budget ceiling."
        },
        {
            "title": "Daily Load Balanced",
            "text": f"{len(trip.attractions)} attractions spread across {num_days} day"
                    f"{'s' if num_days != 1 else ''} (~{avg_per_day} per day), each capped at 8 hours of activity."
        },
        {
            "title": "Walk vs Cab Decided",
            "text": f"{walk_count} leg{'s' if walk_count != 1 else ''} marked walkable (under 800m/12min), "
                    f"{cab_count} recommended by cab for longer distances."
        },
        {
            "title": "Constraints Applied",
            "text": ", ".join(applied_constraints) if applied_constraints
                    else "No specific preferences were captured for this trip."
        },
        {
            "title": "Budget Usage",
            "text": f"Estimated cost ₹{trip.estimated_cost:,.0f} is {budget_pct}% of the ₹{DEFAULT_MAX_BUDGET:,} budget ceiling."
                    if trip.estimated_cost else "Cost could not be estimated for this trip."
        },
    ]


# ── LANDING ───────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ── AUTH ──────────────────────────────────────────────────────

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if get_current_user(request):
        return RedirectResponse("/dashboard", 302)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    email: str    = Form(...),
    password: str = Form(...),
    db: Session   = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid email or password."
        })
    token = create_access_token({"sub": str(user.id), "email": user.email, "name": user.name})
    resp  = RedirectResponse("/dashboard", 302)
    resp.set_cookie("access_token", token, httponly=True, max_age=604800)
    return resp


@app.post("/signup", response_class=HTMLResponse)
def signup(
    request: Request,
    name: str     = Form(...),
    email: str    = Form(...),
    password: str = Form(...),
    db: Session   = Depends(get_db),
):
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Email already registered. Please log in."
        })
    new_user = User(name=name, email=email, hashed_password=hash_password(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = create_access_token({"sub": str(new_user.id), "email": new_user.email, "name": new_user.name})
    resp  = RedirectResponse("/dashboard", 302)
    resp.set_cookie("access_token", token, httponly=True, max_age=604800)
    return resp


@app.get("/logout")
def logout():
    resp = RedirectResponse("/", 302)
    resp.delete_cookie("access_token")
    return resp


# ── DASHBOARD ─────────────────────────────────────────────────

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", 302)

    recent = (
        db.query(Trip)
        .filter(Trip.user_id == int(user["sub"]))
        .order_by(Trip.created_at.desc())
        .limit(6)
        .all()
    )
    return templates.TemplateResponse(
        "dashboard.html",
        base_ctx(request, user, {"recent_trips": recent, "active_page": "dashboard"})
    )


# ── CREATE TRIP ───────────────────────────────────────────────

@app.get("/create", response_class=HTMLResponse)
def create_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", 302)
    return templates.TemplateResponse(
        "create.html",
        base_ctx(request, user, {"active_page": "create"})
    )


# ── HOTEL SELECTION ─────────────────────────────────────────────

@app.post("/select-hotel", response_class=HTMLResponse)
def select_hotel_page(
    request: Request,
    needs: str            = Form(default=""),
    destination: str      = Form(...),
    days: int             = Form(...),
    departure_date: str   = Form(default=""),
    origin: str            = Form(default=""),
    low_walking: str       = Form(default=""),
    budget_strict: str     = Form(default=""),
    elderly: str            = Form(default=""),
    vegetarian: str         = Form(default=""),
    family: str             = Form(default=""),
):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", 302)

    hotels = HotelSearch().search_hotels(destination, departure_date or None, days)

    return templates.TemplateResponse(
        "select_hotel.html",
        base_ctx(request, user, {
            "active_page": "create",
            "destination": destination,
            "days":        days,
            "hotels":      hotels,
            "trip_fields": {
                "needs": needs, "destination": destination, "days": days,
                "departure_date": departure_date, "origin": origin,
                "low_walking": low_walking, "budget_strict": budget_strict,
                "elderly": elderly, "vegetarian": vegetarian, "family": family,
            }
        })
    )


# ── PLAN ─────────────────────────────────────────────────────

@app.get("/plan")
def plan_get_redirect():
    """
    /plan only accepts POST (it's a form submission target). If someone
    reloads the browser while the AI pipeline is still running, the
    resulting GET would otherwise hit FastAPI's raw 405 JSON error —
    redirect to /trips instead, since the in-flight request may well
    have finished and saved a trip in the meantime.
    """
    return RedirectResponse("/trips", 302)


@app.post("/plan", response_class=HTMLResponse)
def create_plan(
    request: Request,
    needs: str            = Form(default=""),
    destination: str      = Form(...),
    days: int             = Form(...),
    departure_date: str   = Form(default=""),
    origin: str            = Form(default=""),
    low_walking: str       = Form(default=""),
    budget_strict: str     = Form(default=""),
    elderly: str            = Form(default=""),
    vegetarian: str         = Form(default=""),
    family: str             = Form(default=""),
    selected_hotel_json: str = Form(default=""),
    db: Session           = Depends(get_db),
):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", 302)

    toggles = {
        "low_walking":    bool(low_walking),
        "budget_strict":  bool(budget_strict),
        "elderly":        bool(elderly),
        "vegetarian":     bool(vegetarian),
        "family":         bool(family),
    }

    selected_hotel = None
    if selected_hotel_json:
        try:
            selected_hotel = json.loads(selected_hotel_json)
        except ValueError:
            selected_hotel = None

    # Use the constraints from this account's most recent trip (if any) as
    # a hint for the LLM, so preferences carry over across trips without a
    # separate memory store — Trip rows are already the source of truth.
    last_trip = (
        db.query(Trip)
        .filter(Trip.user_id == int(user["sub"]))
        .order_by(Trip.created_at.desc())
        .first()
    )
    previous_constraints = last_trip.constraints if last_trip else None

    # Run the full agent pipeline
    result = agent.build_travel_plan(
        needs, destination, days, departure_date or None,
        origin.strip() or "Delhi", toggles, selected_hotel,
        previous_constraints=previous_constraints,
    )

    # Persist to SQLite
    trip = Trip(
        user_id             = int(user["sub"]),
        username            = user["name"],
        destination         = result["destination"],
        days_count          = result["days_count"],
        hotel               = result["hotel"],
        estimated_cost      = result["estimated_cost"],
        constraints_json    = json.dumps(result["constraints"]),
        cost_breakdown_json = json.dumps(result["cost_breakdown"]),
        attractions_json    = json.dumps(result["attractions"]),
        daily_plan_json     = json.dumps(result["daily_plan"]),
        transport_json      = json.dumps(result["transport"]),
        ai_reasoning        = result["ai_reasoning"],
        start_date          = result.get("departure_date"),
        day_dates_json      = json.dumps(result.get("day_dates", [])),
        flights_json        = json.dumps(result.get("flights", [])),
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return RedirectResponse(f"/result/{trip.id}", 302)


# ── RESULT ────────────────────────────────────────────────────

def _trip_context(trip: Trip) -> dict:
    """Fields shared by the dashboard result view and the printable view."""
    return {
        "trip_id":        trip.id,
        "destination":    trip.destination,
        "days_count":     trip.days_count,
        "hotel":          trip.hotel,
        "preferences":    format_preferences(trip.constraints),
        "cost":           trip.estimated_cost,
        "cost_breakdown": trip.cost_breakdown,
        "daily_plan":     trip.daily_plan,
        "attractions":    trip.attractions,
        "transport":      trip.transport,
        "ai_reasoning_html": render_ai_reasoning(trip.ai_reasoning),
        "day_dates":      trip.day_dates,
        "flights":        trip.flights,
    }


def _get_owned_trip(db: Session, user: dict, trip_id: int):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip or trip.user_id != int(user["sub"]):
        return None
    return trip


@app.get("/result/{trip_id}", response_class=HTMLResponse)
def result_page(request: Request, trip_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", 302)

    trip = _get_owned_trip(db, user, trip_id)
    if not trip:
        return RedirectResponse("/dashboard", 302)

    return templates.TemplateResponse(
        "result.html",
        base_ctx(request, user, {
            "active_page": "trips",
            "insights":    build_insights(trip),
            **_trip_context(trip),
        })
    )


@app.get("/result/{trip_id}/print", response_class=HTMLResponse)
def result_print_page(request: Request, trip_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", 302)

    trip = _get_owned_trip(db, user, trip_id)
    if not trip:
        return RedirectResponse("/dashboard", 302)

    return templates.TemplateResponse(
        "result_print.html",
        {"request": request, **_trip_context(trip)}
    )


# ── SAVED TRIPS ───────────────────────────────────────────────

@app.get("/trips", response_class=HTMLResponse)
def trips_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", 302)

    trips = (
        db.query(Trip)
        .filter(Trip.user_id == int(user["sub"]))
        .order_by(Trip.created_at.desc())
        .all()
    )
    return templates.TemplateResponse(
        "trips.html",
        base_ctx(request, user, {"trips": trips, "active_page": "trips"})
    )


@app.post("/trips/{trip_id}/delete")
def delete_trip(request: Request, trip_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", 302)

    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if trip and trip.user_id == int(user["sub"]):
        db.delete(trip)
        db.commit()

    return RedirectResponse("/trips", 302)


# ── PROFILE ───────────────────────────────────────────────────

@app.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", 302)

    db_user = db.query(User).filter(User.id == int(user["sub"])).first()
    return templates.TemplateResponse(
        "profile.html",
        base_ctx(request, user, {
            "active_page":  "profile",
            "email":        user.get("email", ""),
            "member_since": db_user.created_at.strftime("%B %Y") if db_user else "N/A",
        })
    )


# ── PROCESSING (standalone page) ─────────────────────────────

@app.get("/processing", response_class=HTMLResponse)
def processing_page(request: Request):
    return templates.TemplateResponse("processing.html", {"request": request})
