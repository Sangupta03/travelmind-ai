def score_plan(plan_text, constraints):
    """
    Simple heuristic scoring system.
    Later we can replace this with ML or embeddings.
    """

    score = 0

    plan_lower = plan_text.lower()
    constraints_lower = constraints.lower()

    # Budget sensitivity
    if "budget" in constraints_lower and "cheap" in plan_lower:
        score += 3

    # Walking preference
    if "low" in constraints_lower and ("walk" in plan_lower or "walking" in plan_lower):
        score -= 2

    # Comfort indicators
    if "comfortable" in plan_lower or "central hotel" in plan_lower:
        score += 2

    # Experience indicators
    if "sightseeing" in plan_lower or "famous" in plan_lower:
        score += 2

    return score
