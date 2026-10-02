import csv

from window_detector import (
    load_windows,
    build_baseline,
    calculate_window_score,
    get_status
)


NORMAL_FILE = "data/normal_window_features.csv"
TUNNEL_FILE = "data/tunnel_window_features.csv"


def evaluate_windows(windows, baseline, expected):
    results = []

    for window in windows:
        score, signals = calculate_window_score(
            window,
            baseline
        )

        status = get_status(score)
        detected = status in ["HIGH", "CRITICAL"]

        results.append({
            "expected": expected,
            "detected": detected,
            "status": status,
            "score": score,
            "signals": signals
        })

    return results


normal_windows = load_windows(NORMAL_FILE)
tunnel_windows = load_windows(TUNNEL_FILE)

baseline = build_baseline(normal_windows)

normal_results = evaluate_windows(
    normal_windows,
    baseline,
    False
)

tunnel_results = evaluate_windows(
    tunnel_windows,
    baseline,
    True
)

results = normal_results + tunnel_results

tp = sum(r["expected"] and r["detected"] for r in results)
tn = sum(not r["expected"] and not r["detected"] for r in results)
fp = sum(not r["expected"] and r["detected"] for r in results)
fn = sum(r["expected"] and not r["detected"] for r in results)

precision = tp / (tp + fp) if tp + fp else 0
recall = tp / (tp + fn) if tp + fn else 0
fpr = fp / (fp + tn) if fp + tn else 0
fnr = fn / (fn + tp) if fn + tp else 0


print("\n" + "=" * 60)
print("WINDOW-LEVEL DETECTOR EVALUATION")
print("=" * 60)

print("\nDataset Size")
print("-" * 60)
print("Normal windows :", len(normal_windows))
print("Tunnel windows :", len(tunnel_windows))
print("Total windows  :", len(results))

print("\nConfusion Matrix")
print("-" * 60)
print("True Positive  :", tp)
print("True Negative  :", tn)
print("False Positive :", fp)
print("False Negative :", fn)

print("\nMetrics")
print("-" * 60)
print("Precision       :", round(precision * 100, 2), "%")
print("Recall          :", round(recall * 100, 2), "%")
print("False Positive Rate:", round(fpr * 100, 2), "%")
print("False Negative Rate:", round(fnr * 100, 2), "%")


print("\nTunnel Window Results")
print("-" * 60)

for index, result in enumerate(tunnel_results):
    print(
        f"Window {tunnel_windows[index]['window_id']} | "
        f"Score: {result['score']} | "
        f"Status: {result['status']}"
    )


print("\nNormal Window Results")
print("-" * 60)

for index, result in enumerate(normal_results):
    print(
        f"Window {normal_windows[index]['window_id']} | "
        f"Score: {result['score']} | "
        f"Status: {result['status']}"
    )