"""
Eval harness for TravelMind's constraint-extraction step.

This is NOT a pytest unit test — it calls the real Gemini API against a
small set of realistic trip descriptions (see cases.py) and checks
whether the extracted constraints match what a human would expect.

Unit tests (in tests/) check that our own code behaves correctly given
fixed inputs. This checks that the LLM itself behaves correctly, which
can only be verified against the real model, and can drift over time
as the model changes -- that's why it's a separate, manually-run script
rather than something CI runs on every push.

Usage:
    python evals/run_evals.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from agents.user_agent import UserAgent
from evals.cases import CASES

# Fields whose extracted value only needs to *contain* the expected
# word (they're free-text in the schema, e.g. "high budget" vs "high").
# Everything else must match exactly.
FUZZY_FIELDS = {"budget", "food_preference"}


def check_field(actual: dict, field: str, expected) -> bool:
    actual_value = actual.get(field)
    if field in FUZZY_FIELDS:
        return isinstance(actual_value, str) and str(expected).lower() in actual_value.lower()
    return actual_value == expected


def run():
    agent = UserAgent()
    passed = 0
    failed = 0

    for case in CASES:
        result = agent.extract_constraints(case["input"], username="__eval_harness__")

        mismatches = []
        for field, expected in case["expect"].items():
            if not check_field(result, field, expected):
                mismatches.append(f"{field}: expected {expected!r}, got {result.get(field)!r}")

        if mismatches:
            failed += 1
            print(f"FAIL  {case['name']}")
            for m in mismatches:
                print(f"        {m}")
        else:
            passed += 1
            print(f"PASS  {case['name']}")

    total = passed + failed
    print(f"\n{passed}/{total} cases passed")
    return failed == 0


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
