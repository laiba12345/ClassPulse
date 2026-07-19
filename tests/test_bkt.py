from app.bkt import BKTTracker

def test_ten_correct_answers_increase_mastery():
    tracker = BKTTracker(initial_mastery=.25)
    for _ in range(10): tracker.update_mastery("sarah", "fractions", correct=True, ccs=None)
    assert tracker.get("sarah", "fractions") > .9

def test_repeated_incorrect_answers_keep_mastery_low():
    tracker = BKTTracker(initial_mastery=.5)
    for _ in range(8): tracker.update_mastery("sarah", "fractions", correct=False, ccs=None)
    assert tracker.get("sarah", "fractions") < .2

def test_high_ccs_is_modest_soft_evidence():
    explicit = BKTTracker(initial_mastery=.6); soft = BKTTracker(initial_mastery=.6)
    explicit.update_mastery("s", "c", correct=False, ccs=None)
    soft.update_mastery("s", "c", correct=None, ccs=.9)
    assert .6 > soft.get("s", "c") > explicit.get("s", "c")

def test_combined_evidence_is_supported_and_bounded():
    tracker = BKTTracker()
    value = tracker.update_mastery("s", "c", correct=True, ccs=.8)
    assert 0 <= value <= 1
