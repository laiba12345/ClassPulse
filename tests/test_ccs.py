from app.ccs import CCSEngine, SignalWindow

def test_confused_window_scores_above_threshold():
    window = SignalWindow(sentiments=[("confused", .9)] * 3, keyword_flags=3, response_latencies=[28, 31, 35], poll_correct=[False, False, True, False])
    result = CCSEngine().score(window)
    assert result.score > .6
    assert result.poll_miss_rate == .75
    assert result.evidence["confused_lines"] == 3

def test_calm_window_scores_low():
    window = SignalWindow(sentiments=[("positive", .9), ("neutral", .8)], keyword_flags=0, response_latencies=[6, 9], poll_correct=[True, True, True])
    assert CCSEngine().score(window).score < .3

def test_ccs_is_always_bounded():
    engine = CCSEngine()
    extreme = SignalWindow(sentiments=[("confused", 1)] * 100, keyword_flags=100, response_latencies=[999] * 100, poll_correct=[False] * 100)
    assert 0 <= engine.score(extreme).score <= 1
