"""
database.py — SQLAlchemy + SQLite setup
Place this at: travelmind-ai/database.py
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import json

# SQLite file will be created at travelmind-ai/travelmind.db automatically
SQLALCHEMY_DATABASE_URL = "sqlite:///./travelmind.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # needed for SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================
# MODELS
# ============================================================

class User(Base):
    __tablename__ = "users"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String, nullable=False)
    email        = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow)


class Trip(Base):
    __tablename__ = "trips"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, nullable=False, index=True)
    username        = Column(String, nullable=False)
    destination     = Column(String, nullable=False)
    days_count      = Column(Integer, nullable=False)
    hotel           = Column(String)
    estimated_cost  = Column(Float)

    # Store complex objects as JSON strings
    constraints_json     = Column(Text, default="{}")
    cost_breakdown_json  = Column(Text, default="{}")
    attractions_json     = Column(Text, default="[]")
    daily_plan_json      = Column(Text, default="[]")
    transport_json       = Column(Text, default="[]")
    ai_reasoning         = Column(Text, default="")

    created_at = Column(DateTime, default=datetime.utcnow)

    # ---- helper properties so the rest of the app can do trip.cost_breakdown ----

    @property
    def cost_breakdown(self):
        return json.loads(self.cost_breakdown_json or "{}")

    @property
    def constraints(self):
        return json.loads(self.constraints_json or "{}")

    @property
    def attractions(self):
        return json.loads(self.attractions_json or "[]")

    @property
    def daily_plan(self):
        return json.loads(self.daily_plan_json or "[]")

    @property
    def transport(self):
        return json.loads(self.transport_json or "[]")


# ============================================================
# CREATE ALL TABLES (run once on startup)
# ============================================================

def init_db():
    Base.metadata.create_all(bind=engine)


# ============================================================
# DEPENDENCY — use this in FastAPI route functions
# ============================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()