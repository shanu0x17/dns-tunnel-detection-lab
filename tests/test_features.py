from features import (
    query_length,
    max_label_length,
    label_count,
    average_label_length,
    digit_ratio,
    shannon_entropy,
    character_frequency,
    alphabet_distribution
)


query = "NBSWY3DPEB.tunnel.test"


query = "NBSWY3DPEB.tunnel.test"

assert query_length(query) == 22
assert max_label_length(query) == 10
assert label_count(query) == 3
assert average_label_length(query) == 6.666666666666667
assert digit_ratio(query) == 1 / 22
assert character_frequency(query)["N"] == 1
assert character_frequency(query)["B"] == 2
assert alphabet_distribution(query) == 19 / 22

print("All feature tests passed!")