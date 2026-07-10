"""
database.py — SQLAlchemy setup

Uses DATABASE_URL from the environment when set (e.g. a hosted Postgres
instance in production), and falls back to a local SQLite file otherwise.
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import json

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./travelmind.db")

# Some providers (Render, Heroku, Neon) hand out "postgres://" URLs, but
# SQLAlchemy 1.4+ requires the "postgresql://" scheme.
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

_is_sqlite = SQLALCHEMY_DATABASE_URL.startswith("sqlite")

if _is_sqlite:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # pool_pre_ping tests each connection before use and transparently
    # reconnects if it's dead — cloud Postgres providers (Render's free
    # tier included) silently close connections that sit idle for a few
    # minutes, which otherwise surfaces as a 500 on the first request
    # after any period of inactivity.
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=280,
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

    # Raw free-text trip description as typed by the user, and its
    # embedding — used to retrieve semantically similar past trips (RAG)
    # when planning a new one. See core/embeddings.py.
    user_input_text        = Column(Text, nullable=True)
    embedding_json          = Column(Text, nullable=True)

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

    @property
    def embedding(self):
        return json.loads(self.embedding_json) if self.embedding_json else None


# ============================================================
# CREATE ALL TABLES (run once on startup)
# ============================================================

def init_db():
    Base.metadata.create_all(bind=engine)
    # create_all() only creates tables that don't exist yet — it never
    # alters an existing table to add new columns. So this must run for
    # both SQLite and Postgres, not just SQLite: any already-deployed
    # database (e.g. the live Render Postgres instance) still needs
    # these ALTER TABLE statements for columns added after its first deploy.
    _migrate_missing_columns()


def _migrate_missing_columns():
    """Add columns introduced after the trips table already existed."""
    new_columns = {
        "start_date":       "TEXT",
        "day_dates_json":   "TEXT DEFAULT '[]'",
        "flights_json":     "TEXT DEFAULT '[]'",
        "user_input_text":  "TEXT",
        "embedding_json":   "TEXT",
    }
    with engine.connect() as conn:
        if _is_sqlite:
            existing = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(trips)")}
        else:
            existing = {
                row[0] for row in conn.exec_driver_sql(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'trips'"
                )
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