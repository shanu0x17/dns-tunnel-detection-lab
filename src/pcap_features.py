import csv

from scapy.all import rdpcap, DNS, DNSQR

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


fieldnames = [
    "timestamp",
    "domain",
    "query_length",
    "max_label_length",
    "label_count",
    "average_label_length",
    "digit_ratio",
    "shannon_entropy",
    "alphabet_distribution",
    "query_rate",
    "unique_subdomain_ratio",
    "average_inter_arrival",
    "inter_arrival_std",
    "inter_arrival_cv",
    "burstiness",
]


def process_pcap(pcap_file, output_file):

    print("\n" + "=" * 60)
    print("Processing:", pcap_file)
    print("=" * 60)

    packets = rdpcap(pcap_file)

    query_names = []
    timestamps = []

    for packet in packets:

        if (
            packet.haslayer(DNS)
            and packet.haslayer(DNSQR)
            and packet[DNS].qr == 0
        ):
            query_name = packet[DNSQR].qname.decode(errors="ignore")

            query_names.append(query_name)
            timestamps.append(float(packet.time))

    if len(timestamps) > 1:
        duration = timestamps[-1] - timestamps[0]
        rate = query_rate(len(query_names), duration)
    else:
        rate = 0

    unique_ratio = unique_subdomain_ratio(query_names)
    intervals = inter_arrival_times(timestamps)
    avg_inter_arrival = average_inter_arrival_time(timestamps)
    std_inter_arrival = inter_arrival_std(timestamps)
    cv_inter_arrival = inter_arrival_cv(timestamps)
    burstiness_value = burstiness(timestamps)

    with open(output_file, "w", newline="") as feature_csv:

        writer = csv.DictWriter(feature_csv, fieldnames=fieldnames)
        writer.writeheader()

        for index, query_name in enumerate(query_names):

            lexical = extract_features(query_name)

            writer.writerow({
                "timestamp": timestamps[index],
                "domain": query_name,
                "query_length": lexical["query_length"],
                "max_label_length": lexical["max_label_length"],
                "label_count": lexical["label_count"],
                "average_label_length": lexical["average_label_length"],
                "digit_ratio": lexical["digit_ratio"],
                "shannon_entropy": lexical["shannon_entropy"],
                "alphabet_distribution": lexical["alphabet_distribution"],
                "query_rate": rate,
                "unique_subdomain_ratio": unique_ratio,
                "average_inter_arrival": avg_inter_arrival,
                "inter_arrival_std": std_inter_arrival,
                "inter_arrival_cv": cv_inter_arrival,
                "burstiness": burstiness_value
            })

    print("\nQueries captured:", len(query_names))
    print("Query Rate:", round(rate, 4), "queries/second")
    print("Unique Subdomain Ratio:", round(unique_ratio, 4))
    print("Average Inter-arrival:", round(avg_inter_arrival, 4), "seconds")
    print("Inter-arrival Std:", round(std_inter_arrival, 4), "seconds")
    print("Inter-arrival CV:", round(cv_inter_arrival, 4))
    print("Burstiness:", round(burstiness_value, 4))
    print("Saved to:", output_file)


if __name__ == "__main__":

    process_pcap(
        "data/normal_dns.pcap",
        "data/normal_behavioral_features.csv"
    )

    process_pcap(
        "data/dns_tunnel_realistic.pcap",
        "data/tunnel_behavioral_features.csv"
    )