import math



def query_length(query_name):
    return len(query_name)

def max_label_length(query_name):
    labels = query_name.strip(".").split(".")
    return max(len(label) for label in labels)

def label_count(query_name):
    labels = query_name.strip(".").split(".")
    return len(labels)

def average_label_length(query_name):
    labels = query_name.strip(".").split(".")
    total_length = sum(len(label) for label in labels)
    return total_length / len(labels)

def digit_ratio(query_name):
    if len(query_name) == 0:
        return 0

    digit_count = sum(char.isdigit() for char in query_name)

    return digit_count / len(query_name)

def shannon_entropy(text):
    if len(text) == 0:
        return 0

    frequencies = {}

    for char in text:
        frequencies[char] = frequencies.get(char, 0) + 1

    entropy = 0

    for count in frequencies.values():
        probability = count / len(text)
        entropy -= probability * math.log2(probability)

    return entropy

def unique_subdomain_ratio(query_names):
    if len(query_names) == 0:
        return 0

    unique_queries = set(query_names)

    return len(unique_queries) / len(query_names)

def query_rate(query_count, duration):
    if duration <= 0:
        return 0

    return query_count / duration

def inter_arrival_times(timestamps):
    if len(timestamps) < 2:
        return []

    intervals = []

    for i in range(1, len(timestamps)):
        interval = timestamps[i] - timestamps[i - 1]
        intervals.append(interval)

    return intervals

def character_frequency(text):
    frequencies = {}

    for char in text:
        frequencies[char] = frequencies.get(char, 0) + 1

    return frequencies

def alphabet_distribution(text):
    letters = 0

    for char in text:
        if char.isalpha():
            letters += 1

    if len(text) == 0:
        return 0

    return letters / len(text)

def repeated_prefix_ratio(query_names):
    if len(query_names) == 0:
        return 0

    prefixes = []

    for query in query_names:
        labels = query.strip(".").split(".")

        if len(labels) == 0:
            continue

        prefixes.append(labels[0])

    if len(prefixes) == 0:
        return 0

    unique_prefixes = set(prefixes)

    repeated_count = len(prefixes) - len(unique_prefixes)

    return repeated_count / len(prefixes)

def sequence_order_ratio(sequences):
    if len(sequences) < 2:
        return 1

    correct = 0

    for i in range(1, len(sequences)):
        if sequences[i] == sequences[i - 1] + 1:
            correct += 1

    return correct / (len(sequences) - 1)

def average_inter_arrival_time(timestamps):
    intervals = inter_arrival_times(timestamps)

    if len(intervals) == 0:
        return 0

    return sum(intervals) / len(intervals)


def inter_arrival_std(timestamps):
    intervals = inter_arrival_times(timestamps)

    if len(intervals) == 0:
        return 0

    mean = sum(intervals) / len(intervals)

    variance = sum(
        (interval - mean) ** 2
        for interval in intervals
    ) / len(intervals)

    return math.sqrt(variance)


def inter_arrival_cv(timestamps):
    mean = average_inter_arrival_time(timestamps)

    if mean == 0:
        return 0

    std = inter_arrival_std(timestamps)

    return std / mean


def burstiness(timestamps):
    mean = average_inter_arrival_time(timestamps)
    std = inter_arrival_std(timestamps)

    if mean + std == 0:
        return 0

    return (std - mean) / (std + mean)

def extract_features(query_name):
    return {
        "query_length": query_length(query_name),
        "max_label_length": max_label_length(query_name),
        "label_count": label_count(query_name),
        "average_label_length": average_label_length(query_name),
        "digit_ratio": digit_ratio(query_name),
        "shannon_entropy": shannon_entropy(query_name),
        "character_frequency": character_frequency(query_name),
        "alphabet_distribution": alphabet_distribution(query_name),
    }
    


if __name__ == "__main__":
    query = "NBSWY3DPEB.tunnel.test"

    print("Query Length:", query_length(query))
    print("Max Label Length:", max_label_length(query))
    print("Label Count:", label_count(query))
    print("Average Label Length:", average_label_length(query))
    print("Digit Ratio:", digit_ratio(query))
    print("Shannon Entropy:", shannon_entropy(query))
    print("Character Frequency:", character_frequency(query))
    print("Alphabet Distribution:", alphabet_distribution(query))
    
    print("\nCombined Features:")
    print(extract_features(query))