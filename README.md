<div align="center">

# ✈️ TravelMind AI

### Multi-agent AI travel planning — from a sentence to a real itinerary

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-4285F4?logo=googlegemini&logoColor=white)](https://ai.google.dev/)
[![SQLite](https://img.shields.io/badge/DB-SQLite-07405E?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Status](https://img.shields.io/badge/status-active-success)](#)

Describe a trip in plain language. A team of specialized AI agents negotiates a real, day-by-day itinerary — optimized routes, live flight & hotel pricing, walk-vs-cab decisions, and a full budget breakdown.

</div>

---

## Contents

- [Why this is different](#why-this-is-different)
- [Features](#features)
- [Tech stack](#tech-stack)
- [Agent pipeline](#agent-pipeline)
- [Project structure](#project-structure)
- [Setup](#setup)
- [How a trip gets planned](#how-a-trip-gets-planned)
- [Known limitations](#known-limitations)
- [Roadmap](#roadmap)
- [Author](#author)

---

## Why this is different

Most "AI trip planner" demos are a single prompt wrapped in a chat box. TravelMind is a **full web app** with real persistence and real data:

> 🔐 Sign up → 🧭 describe your trip → 🏨 pick a real hotel → 🤖 watch five agents negotiate → 📅 get a real day-by-day plan → 💾 it's saved to your account.

No mock itineraries — flights, hotels, distances, and routes all come from live APIs wherever credentials are configured, with honest, labeled fallbacks when they're not.

---

## Features

| | |
|---|---|
| 🧠 **Multi-agent pipeline** | Budget, Comfort & Experience agents plan **in parallel** (`ThreadPoolExecutor`); a Negotiator merges them, a Manager orchestrates everything |
| ✈️ **Real flight pricing** | Live Amadeus offers when you give a departure date; AviationStack schedules or simulated data otherwise — clearly labeled either way |
| 🌍 **City name resolution** | Type "Bangalore" or "Mumbai" — resolved to real airport codes live via Amadeus, with aliases for renamed Indian cities |
| 🏨 **Pick your own hotel** | Real SerpAPI (Google Hotels) results shown as a selectable list *before* the plan builds — not auto-assigned |
| 📅 **Real day-by-day itinerary** | Attractions split evenly across your actual trip length, nearest-neighbor ordered, with real calendar dates when given a start date |
| 🚕 **Walk vs. cab, per leg** | Computed from real Google Distance Matrix data, grouped by day, with one-tap Google Maps links |
| 💰 **Budget breakdown** | Flights, hotel, transport, food — each tagged live or estimated based on what data was actually available |
| ✨ **Dynamic AI Insights** | Summary cards computed from *your* trip (distance, walk/cab split, applied preferences, budget %) — not canned copy |
| 👤 **Auth + persistence** | JWT auth, bcrypt-hashed passwords, SQLite-backed trips per user, dashboard, deletable saved trips, profile page |

---

## Tech stack

| Layer | Tech |
|---|---|
| Backend | FastAPI, Uvicorn |
| Templates | Jinja2 (server-rendered, no SPA framework) |
| Database | SQLite via SQLAlchemy ORM |
| Auth | JWT (`python-jose`) + bcrypt |
| AI | Gemini 2.5 Flash (`google-genai`) |
| Flights | Amadeus Self-Service API (live pricing) + AviationStack (fallback schedules) |
| Hotels | SerpAPI (Google Hotels engine) |
| Maps & Routing | Google Maps Platform — Geocoding, Places Nearby Search, Distance Matrix |
| Icons | Lucide (SVG icon set, via CDN) |

---

## Agent pipeline

```
                              User input
                                  │
                                  ▼
                              UserAgent
                 extracts structured constraints (budget, walking
                 preference, food, pace, elderly) via Gemini —
                 quick-toggle checkboxes override these deterministically
                                  │
                ┌─────────────────┼─────────────────┐
                ▼                 ▼                 ▼
          BudgetAgent       ComfortAgent      ExperienceAgent
                                                              (run in parallel)
                └─────────────────┼─────────────────┘
                                  ▼
                            NegotiatorAgent
                         merges the three plans
                                  ▼
                            ManagerAgent
        route optimization · daily time-boxing · walk/cab decisions
              budget & constraint validation · structured result
```

---

## Project structure

```text
travelmind-ai/
├── server.py                   # FastAPI app — all routes
├── auth.py                     # JWT + bcrypt
├── database.py                 # SQLAlchemy models (User, Trip) + migrations
├── config.py                   # Loads API keys from .env
│
├── agents/
│   ├── manager_agent.py        # Orchestrates the full pipeline
│   ├── user_agent.py           # Constraint extraction
│   ├── budget_agent.py         # Flights + hotel + low-cost plan
│   ├── comfort_agent.py        # Comfort-optimized plan
│   ├── experience_agent.py     # Experience-optimized plan
│   └── negotiator_agent.py     # Merges the three plans
│
├── core/
│   ├── llm.py                  # Gemini wrapper
│   ├── maps_optimizer.py       # Nearest-neighbor route ordering
│   ├── daily_time_engine.py    # Splits attractions across days
│   ├── transport_engine.py     # Walk vs. cab decision logic
│   ├── walking_estimator.py
│   ├── constraints.py          # Budget ceiling engine
│   ├── validator.py            # Constraint validation
│   └── memory.py               # Per-user profile persistence
│
├── tools/
│   ├── flight_tool.py          # Amadeus / AviationStack / mock flight search
│   ├── hotel_tool.py           # SerpAPI hotel search
│   ├── airport_lookup.py       # City name → IATA code resolution
│   ├── amadeus_client.py       # Amadeus OAuth client
│   ├── attractions_tool.py     # Google Places attraction search
│   ├── maps_tool.py            # Geocoding / Places / Distance Matrix
│   └── route_links.py          # Google Maps deep-link generator
│
├── templates/                  # login, dashboard, create, select_hotel,
│                                # result, trips, profile, sidebar
├── static/style.css
├── requirements.txt
└── .env                        # API keys (not committed)
```

---

## Setup

### 1 · Clone and create a virtual environment

```bash
git clone <repo-url>
cd travelmind-ai
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
```

### 2 · Install dependencies

```bash
pip install -r requirements.txt
```

### 3 · Configure API keys

Copy `.env.example` to `.env` and fill in your own values:

```bash
cp .env.example .env
```

| Key | Required for | If missing |
|---|---|---|
| `JWT_SECRET_KEY` | Signing login sessions | App refuses to start — generate one with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `GEMINI_API_KEY` | Constraint extraction & plan reasoning | App won't function — this is core |
| `GOOGLE_MAPS_KEY` | Attractions, routing, distances | No itinerary/transport data |
| `AMADEUS_API_KEY` / `_SECRET` | Live flight pricing, city → airport lookup | Falls back to AviationStack/mock flights and 3-letter-guess airport codes |
| `SERPAPI_KEY` | Real hotel search & selection | Falls back to a generic "City Center Hotel" placeholder |
| `AVIATIONSTACK_KEY` | Flight schedule fallback (no pricing) | Falls back further to simulated flight data |

Free / sandbox tiers: [Gemini](https://aistudio.google.com) · [Google Maps](https://console.cloud.google.com) · [Amadeus self-service](https://developers.amadeus.com) · [SerpAPI](https://serpapi.com)

### 4 · Run the app

```bash
uvicorn server:app --reload
```

Visit **http://127.0.0.1:8000** → sign up → plan your first trip.

---

## Testing & evaluation

There are two separate layers of automated checking, because they check different things:

- **Unit tests** (`tests/`) — verify our own deterministic code (route optimization, budget math, transport decisions) using mocked API responses. Fast, free, and run automatically in CI on every push:
  ```bash
  pip install -r requirements-dev.txt
  pytest tests/
  ```
- **Eval harness** (`evals/`) — checks whether the *Gemini model itself* correctly extracts structured constraints from realistic free-text trip descriptions (see `evals/cases.py`). This calls the real API, so it's run manually, not in CI:
  ```bash
  python evals/run_evals.py
  ```

---

## How a trip gets planned

1. **Sign up / log in.**
2. **New Trip** — destination, days, optional departure date and "flying from" city, free-text preferences, and quick toggles (low walking, strict budget, vegetarian, elderly, family).
3. **Choose a hotel** — pick from real live hotel results for your destination and dates (auto-falls back gracefully if search comes back empty).
4. **Agents run** — Budget, Comfort, and Experience build independent plans in parallel; the Negotiator merges them; the Manager optimizes the route and schedule.
5. **Review your trip** across five tabs:

   | Tab | What's in it |
   |---|---|
   | Overview | Trip summary, applied preferences, all attractions |
   | Itinerary | Day-by-day plan with real calendar dates |
   | Transport | Walk/cab decision per leg, grouped by day, with Maps links |
   | Budget | Cost breakdown + live/estimated flight & hotel pricing |
   | AI Insights | What the agents actually decided, computed from your real data |

6. **Saved Trips** — every plan persists and can be revisited or deleted from your dashboard.

---

## Known limitations

- Single configurable origin city per trip — no multi-city itineraries yet.
- Amadeus/SerpAPI pricing reflects **test/sandbox** data where applicable — treat as indicative, not bookable.
- Attraction quality depends on what Google Places returns for "tourist attraction" near the destination.

---

## Roadmap

- [ ] Multi-city / multi-leg trips
- [ ] Cross-trip user preference memory (`core/memory.py` lays the groundwork)
- [ ] Booking integration, not just search
- [ ] Mobile-friendly layout pass

---

## Author

**Sanjoli Gupta**


