import csv
import os
from statistics import mean, pstdev

from scapy.all import sniff, DNS, DNSQR
from window_features import calculate_window_features
from config import (
    LOW_THRESHOLD,
    MEDIUM_THRESHOLD,
    HIGH_THRESHOLD,
    LIVE_ENTROPY_WEIGHT,
    LIVE_LONG_LABEL_WEIGHT,
    LIVE_QUERY_RATE_WEIGHT,
    LIVE_UNIQUE_SUBDOMAIN_WEIGHT,
    LIVE_TIMING_WEIGHT
)

BASELINE_FILE = "data/normal_window_features.csv"
LIVE_LOG_FILE = "data/live_windows.csv"
WINDOW_SIZE = 10


def load_baseline():
    data = {}

    with open(BASELINE_FILE, "r", newline="") as file:
        for row in csv.DictReader(file):
            for key, value in row.items():
                if key != "window_id" and value != "":
                    data.setdefault(key, []).append(float(value))

    return {
        key: {"mean": mean(values), "std": pstdev(values)}
        for key, values in data.items()
    }


def score_signal(value, baseline, weight):
    if value is None or baseline["std"] == 0:
        return 0

    z = abs(value - baseline["mean"]) / baseline["std"]

    if z < 1.5:
        return 0
    if z < 2.5:
        return weight * 0.4
    if z < 3.5:
        return weight * 0.7

    return weight


def handle_packet(packet, queries):
    if packet.haslayer(DNS) and packet.haslayer(DNSQR):
        if packet[DNS].qr == 0:
            queries.append({
                "timestamp": float(packet.time),
                "domain": packet[DNSQR].qname.decode(errors="ignore")
            })


def detect_window(features, baseline):
    signals = {}

    signals["entropy"] = score_signal(
        features["average_entropy"],
        baseline["average_entropy"],
        LIVE_ENTROPY_WEIGHT
    )

    signals["long_label"] = score_signal(
        features["average_label_length"],
        baseline["average_label_length"],
        LIVE_LONG_LABEL_WEIGHT
    )

    signals["query_rate"] = score_signal(
        features["query_rate"],
        baseline["query_rate"],
        LIVE_QUERY_RATE_WEIGHT
    )

    signals["unique_subdomain"] = score_signal(
        features["unique_subdomain_ratio"],
        baseline["unique_subdomain_ratio"],
        LIVE_UNIQUE_SUBDOMAIN_WEIGHT
    )

    timing_cv = score_signal(
        features["inter_arrival_cv"],
        baseline["inter_arrival_cv"],
        LIVE_TIMING_WEIGHT / 2
    )

    timing_burst = score_signal(
        features["burstiness"],
        baseline["burstiness"],
        LIVE_TIMING_WEIGHT / 2
    )

    signals["timing"] = min(
        LIVE_TIMING_WEIGHT,
        timing_cv + timing_burst
    )

    raw_score = sum(signals.values())

    suspicious = sum(
        value > 0
        for value in signals.values()
    )

    if suspicious < 2:
        score = min(raw_score, 29)

    elif suspicious == 2:
        score = min(raw_score, 59)

    else:
        score = min(raw_score, 100)

    if score >= HIGH_THRESHOLD:
        status = "CRITICAL"

    elif score >= MEDIUM_THRESHOLD:
        status = "HIGH"

    elif score >= LOW_THRESHOLD:
        status = "MEDIUM"

    else:
        status = "LOW"

    signals = {
        key: round(value, 2)
        for key, value in signals.items()
    }

    return round(score, 2), status, signals


def initialize_live_log():
    os.makedirs("data", exist_ok=True)

    fields = [
        "timestamp", "query_count", "query_rate",
        "average_entropy", "average_label_length",
        "unique_subdomain_ratio", "inter_arrival_cv",
        "burstiness", "score", "status",
        "entropy_signal", "long_label_signal",
        "query_rate_signal", "unique_subdomain_signal",
        "timing_signal"
    ]

    if not os.path.exists(LIVE_LOG_FILE):
        with open(LIVE_LOG_FILE, "w", newline="") as file:
            csv.DictWriter(file, fieldnames=fields).writeheader()


def log_live_window(features, score, status, signals):
    fields = [
        "timestamp", "query_count", "query_rate",
        "average_entropy", "average_label_length",
        "unique_subdomain_ratio", "inter_arrival_cv",
        "burstiness", "score", "status",
        "entropy_signal", "long_label_signal",
        "query_rate_signal", "unique_subdomain_signal",
        "timing_signal"
    ]

    row = {
        "timestamp": __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "query_count": features["query_count"],
        "query_rate": round(features["query_rate"], 3),
        "average_entropy": round(features["average_entropy"], 3),
        "average_label_length": round(features["average_label_length"], 3),
        "unique_subdomain_ratio": round(features["unique_subdomain_ratio"], 3),
        "inter_arrival_cv": round(features["inter_arrival_cv"], 3),
        "burstiness": round(features["burstiness"], 3),
        "score": score,
        "status": status,
        "entropy_signal": signals["entropy"],
        "long_label_signal": signals["long_label"],
        "query_rate_signal": signals["query_rate"],
        "unique_subdomain_signal": signals["unique_subdomain"],
        "timing_signal": signals["timing"]
    }

    with open(LIVE_LOG_FILE, "a", newline="") as file:
        csv.DictWriter(file, fieldnames=fields).writerow(row)


print("\n" + "=" * 50)
print("LIVE DNS TUNNEL DETECTION")
print("=" * 50)

baseline = load_baseline()
initialize_live_log()

print("\nBaseline loaded.")
print("Live log:", LIVE_LOG_FILE)
print("Listening on UDP/5353...")
print("Window size:", WINDOW_SIZE, "seconds")
print("\nGenerate DNS traffic now...\n")


while True:
    queries = []

    sniff(
        iface=r"\Device\NPF_Loopback",
        filter="udp port 5353",
        prn=lambda packet: handle_packet(packet, queries),
        store=False,
        timeout=WINDOW_SIZE
    )

    if not queries:
        print("No DNS queries detected in this window.")
        continue

    features = calculate_window_features(queries)
    score, status, signals = detect_window(features, baseline)

    log_live_window(
        features,
        score,
        status,
        signals
    )

    print("\n" + "-" * 50)
    print("LIVE WINDOW")
    print("-" * 50)

    print("Queries:", features["query_count"])
    print("Query Rate:", round(features["query_rate"], 3), "q/s")
    print("Entropy:", round(features["average_entropy"], 3))
    print("Avg Label Length:", round(features["average_label_length"], 3))
    print("Unique Ratio:", round(features["unique_subdomain_ratio"], 3))
    print("Inter-arrival CV:", round(features["inter_arrival_cv"], 3))
    print("Burstiness:", round(features["burstiness"], 3))

    print("\nDetection Score:", score)
    print("Status:", status)

    print("\nSignal Contributions:")

    for signal, value in signals.items():
        print(" ", signal + ":", value)

    if status in ["HIGH", "CRITICAL"]:
        print("\n🚨 ALERT: Suspicious DNS behavior detected!")

    print("\nSaved to:", LIVE_LOG_FILE)
    print("-" * 50)