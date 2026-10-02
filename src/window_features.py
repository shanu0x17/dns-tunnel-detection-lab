import csv

from features import (
    extract_features,
    query_rate,
    unique_subdomain_ratio,
    inter_arrival_times,
    average_inter_arrival_time,
    inter_arrival_std,
    inter_arrival_cv,
    burstiness
)

WINDOW_SIZE = 10


def load_queries(filename):
    queries = []

    with open(filename, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            queries.append({
                "timestamp": float(row["timestamp"]),
                "domain": row["domain"]
            })

    return queries


def create_windows(queries):
    if not queries:
        return []

    queries.sort(key=lambda x: x["timestamp"])

    windows = []
    start_time = queries[0]["timestamp"]
    current_window = []

    for query in queries:
        if query["timestamp"] - start_time < WINDOW_SIZE:
            current_window.append(query)
        else:
            if current_window:
                windows.append(current_window)

            start_time = query["timestamp"]
            current_window = [query]

    if current_window:
        windows.append(current_window)

    return windows


def calculate_window_features(window):
    domains = [query["domain"] for query in window]
    timestamps = [query["timestamp"] for query in window]

    lexical_features = [extract_features(domain) for domain in domains]

    average_entropy = sum(
        feature["shannon_entropy"] for feature in lexical_features
    ) / len(lexical_features)

    average_query_length = sum(
        feature["query_length"] for feature in lexical_features
    ) / len(lexical_features)

    average_label_length = sum(
        feature["max_label_length"] for feature in lexical_features
    ) / len(lexical_features)

    rate = query_rate(
        len(domains),
        max(timestamps[-1] - timestamps[0], 0.001)
    )

    unique_ratio = unique_subdomain_ratio(domains)

    return {
        "query_count": len(domains),
        "average_query_length": average_query_length,
        "average_label_length": average_label_length,
        "average_entropy": average_entropy,
        "query_rate": rate,
        "unique_subdomain_ratio": unique_ratio,
        "average_inter_arrival": average_inter_arrival_time(timestamps),
        "inter_arrival_std": inter_arrival_std(timestamps),
        "inter_arrival_cv": inter_arrival_cv(timestamps),
        "burstiness": burstiness(timestamps)
    }


def process_dataset(input_file, output_file):
    queries = load_queries(input_file)
    windows = create_windows(queries)

    fieldnames = [
        "window_id",
        "query_count",
        "average_query_length",
        "average_label_length",
        "average_entropy",
        "query_rate",
        "unique_subdomain_ratio",
        "average_inter_arrival",
        "inter_arrival_std",
        "inter_arrival_cv",
        "burstiness"
    ]

    with open(output_file, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for index, window in enumerate(windows):
            features = calculate_window_features(window)
            writer.writerow({
                "window_id": index,
                **features
            })

    print(output_file, "created with", len(windows), "windows.")


if __name__ == "__main__":
    process_dataset(
        "data/normal_behavioral_features.csv",
        "data/normal_window_features.csv"
    )

    process_dataset(
        "data/tunnel_behavioral_features.csv",
        "data/tunnel_window_features.csv"
    )