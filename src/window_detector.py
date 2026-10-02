import csv
import math
from statistics import mean, pstdev

from config import (
    ENTROPY_WEIGHT,
    LONG_LABEL_WEIGHT,
    QUERY_RATE_WEIGHT,
    UNIQUE_SUBDOMAIN_WEIGHT,
    TIMING_WEIGHT,
    LOW_THRESHOLD,
    MEDIUM_THRESHOLD,
    HIGH_THRESHOLD
)

NORMAL_FILE = "data/normal_window_features.csv"
TUNNEL_FILE = "data/tunnel_window_features.csv"


FEATURES = [
    "average_entropy",
    "average_label_length",
    "query_rate",
    "unique_subdomain_ratio",
    "inter_arrival_cv",
    "burstiness"
]


def load_windows(filename):
    windows = []

    with open(filename, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            window = {}

            for feature in FEATURES:
                window[feature] = float(row[feature])

            window["window_id"] = int(row["window_id"])
            window["query_count"] = int(row["query_count"])

            windows.append(window)

    return windows


def build_baseline(windows):
    fields = [
        "average_entropy",
        "average_label_length",
        "query_rate",
        "unique_subdomain_ratio",
        "inter_arrival_cv",
        "burstiness"
    ]

    baseline = {}

    for field in fields:
        values = [float(row[field]) for row in windows]
        baseline[field] = {
            "mean": mean(values),
            "std": pstdev(values) if len(values) > 1 else 0
        }

    return baseline


def calculate_z_score(value, mean_value, std_value):
    if std_value == 0:
        return 0

    return abs(value - mean_value) / std_value


def score_feature(value, baseline, feature, weight):
    z_score = calculate_z_score(
        value,
        baseline[feature]["mean"],
        baseline[feature]["std"]
    )

    return min(weight, (z_score / 3) * weight)


def calculate_window_score(window, baseline):
    signals = {}

    signals["entropy"] = score_feature(
        window["average_entropy"],
        baseline,
        "average_entropy",
        ENTROPY_WEIGHT
    )

    signals["long_label"] = score_feature(
        window["average_label_length"],
        baseline,
        "average_label_length",
        LONG_LABEL_WEIGHT
    )

    signals["query_rate"] = score_feature(
        window["query_rate"],
        baseline,
        "query_rate",
        QUERY_RATE_WEIGHT
    )

    signals["unique_subdomain"] = score_feature(
        window["unique_subdomain_ratio"],
        baseline,
        "unique_subdomain_ratio",
        UNIQUE_SUBDOMAIN_WEIGHT
    )

    cv_score = score_feature(
        window["inter_arrival_cv"],
        baseline,
        "inter_arrival_cv",
        10
    )

    burstiness_score = score_feature(
        window["burstiness"],
        baseline,
        "burstiness",
        10
    )

    signals["timing"] = min(
    TIMING_WEIGHT,
    cv_score + burstiness_score
)

    raw_score = sum(signals.values())
    score = min(100, (raw_score / 70) * 100)

    return round(score, 2), {
        key: round(value, 2)
        for key, value in signals.items()
    }


def get_status(score):
    if score >= HIGH_THRESHOLD:
        return "CRITICAL"

    if score >= MEDIUM_THRESHOLD:
        return "HIGH"

    if score >= LOW_THRESHOLD:
        return "MEDIUM"

    return "LOW"


def analyze_windows():
    normal_windows = load_windows(NORMAL_FILE)
    tunnel_windows = load_windows(TUNNEL_FILE)

    baseline = build_baseline(normal_windows)

    print("\n" + "=" * 65)
    print("WINDOW-LEVEL DNS TUNNEL DETECTION")
    print("=" * 65)

    print("\nNormal baseline windows:", len(normal_windows))
    print("Tunnel windows:", len(tunnel_windows))

    print("\n" + "-" * 65)
    print("TUNNEL WINDOW RESULTS")
    print("-" * 65)

    for window in tunnel_windows:
        score, signals = calculate_window_score(window, baseline)
        status = get_status(score)

        print(f"\nWindow: {window['window_id']}")
        print(f"Queries: {window['query_count']}")
        print(f"Score: {score}")
        print(f"Status: {status}")
        print(f"Signals: {signals}")

    print("\n" + "-" * 65)
    print("NORMAL WINDOW CHECK")
    print("-" * 65)

    for window in normal_windows:
        score, signals = calculate_window_score(window, baseline)
        status = get_status(score)

        print(
            f"Window {window['window_id']} | "
            f"Queries: {window['query_count']} | "
            f"Score: {score} | "
            f"Status: {status}"
        )


if __name__ == "__main__":
    analyze_windows()