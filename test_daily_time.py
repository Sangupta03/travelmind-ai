from core.daily_time_engine import DailyTimeEngine

engine = DailyTimeEngine(max_hours_per_day=8)

places = [
    "Amber Fort Jaipur",
    "Hawa Mahal",
    "City Palace Jaipur",
    "Jantar Mantar Jaipur",
    "Albert Hall Museum",
    "Nahargarh Fort"
]

days = engine.build_daily_plan("Jaipur", places)

for i, day in enumerate(days, 1):
    print(f"\nDay {i}")
    for p in day:
        print(p)
