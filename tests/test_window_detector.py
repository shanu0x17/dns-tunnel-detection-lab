from window_detector import (
    build_baseline,
    calculate_window_score,
    get_status
)


def make_window(
    entropy=3.0,
    label_length=6.0,
    query_rate=1.5,
    unique_ratio=0.5,
    inter_arrival_cv=0.4,
    burstiness=-0.4
):
    return {
        "average_entropy": entropy,
        "average_label_length": label_length,
        "query_rate": query_rate,
        "unique_subdomain_ratio": unique_ratio,
        "inter_arrival_cv": inter_arrival_cv,
        "burstiness": burstiness
    }


def test_build_baseline():
    windows = [
        make_window(),
        make_window(),
        make_window()
    ]

    baseline = build_baseline(windows)

    assert "average_entropy" in baseline
    assert "query_rate" in baseline
    assert "unique_subdomain_ratio" in baseline


def test_window_score_is_bounded():
    baseline = build_baseline([
        make_window(),
        make_window(),
        make_window()
    ])

    score, signals = calculate_window_score(
        make_window(
            entropy=5.0,
            label_length=12.0,
            query_rate=5.0,
            unique_ratio=1.0,
            inter_arrival_cv=1.5,
            burstiness=0.5
        ),
        baseline
    )

    assert 0 <= score <= 100
    assert isinstance(signals, dict)


def test_normal_window_has_low_or_medium_score():
    windows = [
        make_window(),
        make_window(),
        make_window()
    ]

    baseline = build_baseline(windows)

    score, _ = calculate_window_score(
        make_window(),
        baseline
    )

    assert score < 60


def test_suspicious_window_scores_higher():
    normal = [
        make_window(),
        make_window(),
        make_window()
    ]

    baseline = build_baseline(normal)

    normal_score, _ = calculate_window_score(
        normal[0],
        baseline
    )

    suspicious = make_window(
        entropy=5.0,
        label_length=12.0,
        query_rate=5.0,
        unique_ratio=1.0,
        inter_arrival_cv=1.5,
        burstiness=0.5
    )

    suspicious_score, _ = calculate_window_score(
        suspicious,
        baseline
    )

    assert suspicious_score >= normal_score


def test_status_levels():
    assert get_status(10) == "LOW"
    assert get_status(40) == "MEDIUM"
    assert get_status(70) == "HIGH"
    assert get_status(90) == "CRITICAL"