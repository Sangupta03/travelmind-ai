from core.validator import ConstraintValidator


def test_empty_plan_is_invalid():
    validator = ConstraintValidator()
    assert validator.validate({"walking_preference": "low"}, "") is False


def test_low_walking_preference_rejects_trekking_plan():
    validator = ConstraintValidator()
    constraints = {"walking_preference": "low"}
    plan = "Day 1: A scenic trek through the hills."
    assert validator.validate(constraints, plan) is False


def test_low_walking_preference_rejects_long_walk_plan():
    validator = ConstraintValidator()
    constraints = {"walking_preference": "low"}
    plan = "Day 1: Enjoy a long walk along the beach."
    assert validator.validate(constraints, plan) is False


def test_vegetarian_preference_rejects_non_veg_plan():
    validator = ConstraintValidator()
    constraints = {"food_preference": "vegetarian"}
    plan = "Day 1: Try the local non-veg specialties."
    assert validator.validate(constraints, plan) is False


def test_plan_passes_when_no_constraint_is_violated():
    validator = ConstraintValidator()
    constraints = {"walking_preference": "low", "food_preference": "vegetarian"}
    plan = "Day 1: Relax at a rooftop cafe and enjoy vegetarian food."
    assert validator.validate(constraints, plan) is True
