"""
API Diagnostic Script
Run this inside your travelmind-ai venv:
python check_apis.py
"""
import os, sys, requests
from dotenv import load_dotenv
load_dotenv()

GOOGLE_MAPS_KEY = os.getenv("GOOGLE_MAPS_KEY")
SERPAPI_KEY     = os.getenv("SERPAPI_KEY")
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY")

print("=" * 55)
print("  TRAVELMIND API DIAGNOSTIC")
print("=" * 55)

# ── 1. KEY PRESENCE ───────────────────────────────────────
print("\n📋 API KEY PRESENCE:")
print(f"  GOOGLE_MAPS_KEY : {'✅ Found' if GOOGLE_MAPS_KEY else '❌ MISSING in .env'}")
print(f"  SERPAPI_KEY     : {'✅ Found' if SERPAPI_KEY     else '❌ MISSING in .env'}")
print(f"  GEMINI_API_KEY  : {'✅ Found' if GEMINI_API_KEY  else '❌ MISSING in .env'}")

# ── 2. GOOGLE MAPS GEOCODE ────────────────────────────────
print("\n🗺  GOOGLE MAPS — Geocode API:")
if GOOGLE_MAPS_KEY:
    try:
        r = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"address": "Jaipur, India", "key": GOOGLE_MAPS_KEY},
            timeout=10
        ).json()
        status = r.get("status")
        if status == "OK":
            loc = r["results"][0]["geometry"]["location"]
            print(f"  ✅ Working — Jaipur coords: {loc['lat']:.4f}, {loc['lng']:.4f}")
        else:
            print(f"  ❌ Failed — status: {status}")
            em = r.get("error_message", "No error message")
            print(f"     Error: {em}")
    except Exception as e:
        print(f"  ❌ Exception: {e}")
else:
    print("  ⏭  Skipped — key missing")

# ── 3. GOOGLE MAPS NEARBY PLACES ─────────────────────────
print("\n📍 GOOGLE MAPS — Nearby Places API:")
if GOOGLE_MAPS_KEY:
    try:
        r = requests.get(
            "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
            params={
                "location": "26.9124,75.7873",
                "radius": 8000,
                "keyword": "tourist attraction",
                "key": GOOGLE_MAPS_KEY
            },
            timeout=10
        ).json()
        status = r.get("status")
        if status == "OK":
            results = r.get("results", [])
            print(f"  ✅ Working — Found {len(results)} places near Jaipur")
            for p in results[:3]:
                print(f"     • {p['name']}")
        else:
            print(f"  ❌ Failed — status: {status}")
            em = r.get("error_message", "No error message")
            print(f"     Error: {em}")
    except Exception as e:
        print(f"  ❌ Exception: {e}")
else:
    print("  ⏭  Skipped — key missing")

# ── 4. GOOGLE MAPS DISTANCE MATRIX ───────────────────────
print("\n🚗 GOOGLE MAPS — Distance Matrix API:")
if GOOGLE_MAPS_KEY:
    try:
        r = requests.get(
            "https://maps.googleapis.com/maps/api/distancematrix/json",
            params={
                "origins": "Hawa Mahal, Jaipur",
                "destinations": "Amber Fort, Jaipur",
                "mode": "driving",
                "key": GOOGLE_MAPS_KEY
            },
            timeout=10
        ).json()
        status = r.get("status")
        if status == "OK":
            elem = r["rows"][0]["elements"][0]
            if elem["status"] == "OK":
                print(f"  ✅ Working — Hawa Mahal → Amber Fort: {elem['distance']['text']}, {elem['duration']['text']}")
            else:
                print(f"  ❌ Element status: {elem['status']}")
        else:
            print(f"  ❌ Failed — status: {status}")
            em = r.get("error_message", "")
            print(f"     Error: {em}")
    except Exception as e:
        print(f"  ❌ Exception: {e}")
else:
    print("  ⏭  Skipped — key missing")

# ── 5. SERPAPI HOTELS ─────────────────────────────────────
print("\n🏨 SERPAPI — Hotels:")
if SERPAPI_KEY:
    try:
        r = requests.get(
            "https://serpapi.com/search.json",
            params={
                "engine": "google_hotels",
                "q": "hotels in Jaipur",
                "check_in_date": "2026-07-01",
                "check_out_date": "2026-07-04",
                "adults": 2,
                "currency": "INR",
                "api_key": SERPAPI_KEY
            },
            timeout=15
        ).json()
        if "error" in r:
            print(f"  ❌ Failed — {r['error']}")
        else:
            hotels = r.get("properties", [])
            print(f"  ✅ Working — Found {len(hotels)} hotels")
            for h in hotels[:2]:
                print(f"     • {h['name']}")
    except Exception as e:
        print(f"  ❌ Exception: {e}")
else:
    print("  ⏭  Skipped — key missing")

print("\n" + "=" * 55)
print("  Fix: enable missing APIs in Google Cloud Console")
print("  Required APIs: Maps Geocoding, Places, Distance Matrix")
print("=" * 55)