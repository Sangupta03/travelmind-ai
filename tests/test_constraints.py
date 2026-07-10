from core.constraints import BudgetEngine, DEFAULT_MAX_BUDGET


def test_calculate_total_cost_sums_all_parts():
    engine = BudgetEngine()
    total = engine.calculate_total_cost(
        flight_cost=5000, hotel_cost=10000, local_cost=2000, food_cost=3000
    )
    assert total == 20000


def test_is_within_budget_true_when_under_limit():
    engine = BudgetEngine(max_budget=50000)
    assert engine.is_within_budget(49999) is True


def test_is_within_budget_true_when_equal_to_limit():
    engine = BudgetEngine(max_budget=50000)
    assert engine.is_within_budget(50000) is True


def test_is_within_budget_false_when_over_limit():
    engine = BudgetEngine(max_budget=50000)
    assert engine.is_within_budget(50001) is False


def test_default_max_budget_used_when_not_specified():
    engine = BudgetEngine()
    assert engine.max_budget == DEFAULT_MAX_BUDGET
