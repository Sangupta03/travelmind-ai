from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from agents.manager_agent import ManagerAgent

app = FastAPI()
agent = ManagerAgent()

# Static + templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# =========================================================

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


# =========================================================

@app.post("/plan", response_class=HTMLResponse)
def create_plan(
    request: Request,
    name: str = Form(...),
    needs: str = Form(...),
    destination: str = Form(...),
    days: int = Form(...)
):

    result = agent.build_travel_plan(
        name,
        needs,
        destination,
        days
    )

    # ✅ NEW — pass structured data to UI
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,

            # core
            "plan": result["final_plan"],
            "constraints": result["constraints"],
            "cost": result["estimated_cost"],

            # NEW dashboard data
            "hotel": result["hotel"],
            "daily": result["daily_plan"],
            "places": result["ordered_places"],
            "transport": result["transport"]
        }
    )
