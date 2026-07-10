from core.scoring import score_plan


def test_cheap_plan_scores_higher_for_budget_conscious_traveler():
    score = score_plan("A cheap and simple itinerary.", "tight budget")
    assert score == 3


def test_walking_plan_scores_lower_for_low_walking_preference():
    score = score_plan("Lots of walking between sights.", "low walking preference")
    assert score == -2


def test_comfortable_plan_gets_comfort_bonus():
    score = score_plan("Stay at a comfortable central hotel.", "no special preference")
    assert score == 2


def test_sightseeing_plan_gets_experience_bonus():
    score = score_plan("Visit famous sightseeing spots.", "no special preference")
    assert score == 2


def test_scores_are_combined_when_multiple_signals_present():
    score = score_plan("A cheap plan with famous sightseeing.", "tight budget")
    assert score == 5
