"""
TravelMind AI — FastAPI Server
Handles all routes for the new multi-page frontend.
"""

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import json

from agents.manager_agent import ManagerAgent

app = FastAPI(title="TravelMind AI")
agent = ManagerAgent()

# Static + templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# In-memory trip store (replace with a database in production)
trip_store: dict = {}
trip_counter = {"n": 0}


# ============================================================
# LANDING
# ============================================================

@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ============================================================
# AUTH (stub — wire to real auth system as needed)
# ============================================================

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
def login_submit(request: Request, email: str = Form(...), password: str = Form(...)):
    # TODO: Replace with real auth. For now, derive username from email.
    username = email.split("@")[0]
    # Store username in a simple cookie (use sessions in production)
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie("username", username)
    return response


@app.post("/signup", response_class=HTMLResponse)
def signup_submit(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    username = name.split()[0] if name else email.split("@")[0]
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie("username", username)
    return response


@app.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("username")
    return response


# ============================================================
# DASHBOARD
# ============================================================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    username = request.cookies.get("username", "Traveler")
    # Collect saved trips for this user
    recent = [
        {**v, "id": k}
        for k, v in trip_store.items()
        if v.get("username") == username
    ][-5:]  # last 5
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "username": username,
        "recent_trips": recent
    })


# ============================================================
# CREATE TRIP
# ============================================================

@app.get("/create", response_class=HTMLResponse)
def create_page(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})


# ============================================================
# PLAN (SUBMIT FORM)
# Redirects through processing screen, then shows result.
# ============================================================

@app.post("/plan", response_class=HTMLResponse)
def create_plan(
    request: Request,
    name: str = Form(...),
    needs: str = Form(...),
    destination: str = Form(...),
    days: int = Form(...)
):
    # Run the agent pipeline
    result = agent.build_travel_plan(name, needs, destination, days)

    # Store trip
    trip_counter["n"] += 1
    tid = str(trip_counter["n"])
    trip_store[tid] = {
        "username": name,
        "destination": result["destination"],
        "days": result["days_count"],
        "hotel": result["hotel"],
        "cost": result["estimated_cost"],
        "date": "Today",
        **result
    }

    return RedirectResponse(url=f"/result/{tid}", status_code=302)


# ============================================================
# RESULT PAGE
# ============================================================

@app.get("/result/{trip_id}", response_class=HTMLResponse)
def result_page(request: Request, trip_id: str):
    trip = trip_store.get(trip_id)
    if not trip:
        return RedirectResponse(url="/dashboard", status_code=302)

    return templates.TemplateResponse("result.html", {
        "request": request,
        "destination": trip["destination"],
        "days_count": trip["days_count"],
        "hotel": trip["hotel"],
        "constraints": trip["constraints"],
        "cost": trip["estimated_cost"],
        "cost_breakdown": trip["cost_breakdown"],
        "daily_plan": trip["daily_plan"],
        "attractions": trip["attractions"],
        "transport": trip["transport"],
        "ai_reasoning": trip["ai_reasoning"]
    })


# ============================================================
# SAVED TRIPS
# ============================================================

@app.get("/trips", response_class=HTMLResponse)
def trips_page(request: Request):
    username = request.cookies.get("username", "Traveler")
    trips = [
        {**v, "id": k}
        for k, v in trip_store.items()
        if v.get("username") == username
    ]
    return templates.TemplateResponse("trips.html", {
        "request": request,
        "trips": trips
    })


# ============================================================
# PROFILE
# ============================================================

@app.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request):
    username = request.cookies.get("username", "Traveler")
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "username": username
    })


# ============================================================
# PROCESSING SCREEN (optional standalone page)
# ============================================================

@app.get("/processing", response_class=HTMLResponse)
def processing_page(request: Request):
    return templates.TemplateResponse("processing.html", {"request": request})


# ============================================================
# Run: uvicorn server:app --reload
# ============================================================
