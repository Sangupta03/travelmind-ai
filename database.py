"""
database.py — SQLAlchemy + SQLite setup

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

    # Optional trip start date (user-provided) and derived per-day calendar labels
    start_date            = Column(String, nullable=True)
    day_dates_json        = Column(Text, default="[]")
    flights_json          = Column(Text, default="[]")

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

    @property
    def day_dates(self):
        return json.loads(self.day_dates_json or "[]")

    @property
    def flights(self):
        return json.loads(self.flights_json or "[]")


# ============================================================
# CREATE ALL TABLES (run once on startup)
# ============================================================

def init_db():
    Base.metadata.create_all(bind=engine)
    _migrate_missing_columns()


def _migrate_missing_columns():
    """Add columns introduced after a trips table already existed (SQLite has no ALTER ... IF NOT EXISTS)."""
    with engine.connect() as conn:
        existing = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(trips)")}
        new_columns = {
            "start_date":     "TEXT",
            "day_dates_json": "TEXT DEFAULT '[]'",
            "flights_json":   "TEXT DEFAULT '[]'",
        }
        for col, coltype in new_columns.items():
            if col not in existing:
                conn.exec_driver_sql(f"ALTER TABLE trips ADD COLUMN {col} {coltype}")
        conn.commit()


# ============================================================
# DEPENDENCY — use this in FastAPI route functions
# ============================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()