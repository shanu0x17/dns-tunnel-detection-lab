import base64
import re

def encode_base32(message):
    data = message.encode("utf-8")
    encoded = base64.b32encode(data)

    return encoded.decode("ascii").rstrip("=")


def decode_base32(encoded_message):
    padding = "=" * ((8 - len(encoded_message) % 8) % 8)

    encoded_message = encoded_message + padding

    data = encoded_message.encode("ascii")
    decoded = base64.b32decode(data)

    return decoded.decode("utf-8")


def chunk_payload(encoded_data, chunk_size=10):
    chunks = []

    for i in range(0, len(encoded_data), chunk_size):
        chunk = encoded_data[i:i + chunk_size]
        chunks.append(chunk)

    return chunks

def build_query_name(session_id, sequence, total_chunks, payload, lab_domain):
    return (
        f"v1."
        f"{session_id}."
        f"{sequence:04d}."
        f"{total_chunks:04d}."
        f"{payload}."
        f"{lab_domain}"
    )
    
def parse_query_name(query_name):
    parts = query_name.split(".")

    # Check number of fields
    if len(parts) != 7:
        raise ValueError("Invalid query format")

    version = parts[0]
    session_id = parts[1]
    sequence_text = parts[2]
    total_text = parts[3]
    payload = parts[4]
    lab_domain = ".".join(parts[5:])

    # Check protocol version
    if version != "v1":
        raise ValueError("Unsupported protocol version")

    # Check lab namespace
    if lab_domain != "tunnel.test":
        raise ValueError("Invalid lab namespace")

    # Convert sequence and total to integers
    try:
        sequence = int(sequence_text)
        total_chunks = int(total_text)
    except ValueError:
        raise ValueError("Sequence and total must be numbers")

    # Check sequence range
    if sequence < 0:
        raise ValueError("Invalid sequence number")

    if total_chunks <= 0:
        raise ValueError("Invalid total chunks")

    if sequence >= total_chunks:
        raise ValueError("Sequence number exceeds total chunks")

    # Check payload
    if not payload:
        raise ValueError("Empty payload")

    # Validate Base32 payload with regular expression module
    if not re.fullmatch(r"[A-Z2-7]+", payload):
        raise ValueError("Invalid Base32 payload")

    return {
        "version": version,
        "session_id": session_id,
        "sequence": sequence,
        "total_chunks": total_chunks,
        "payload": payload,
        "lab_domain": lab_domain
    }
    
def reassemble_chunks(chunks, total_chunks):
    received = {}

    for sequence, payload in chunks:

        # Ignore exact duplicate sequence numbers
        if sequence in received:
            continue

        received[sequence] = payload

    # Check for missing chunks
    missing = []

    for i in range(total_chunks):
        if i not in received:
            missing.append(i)

    if missing:
        return {
            "status": "INCOMPLETE",
            "missing_sequences": missing
        }

    # Reconstruct in sequence order
    ordered_payload = ""

    for i in range(total_chunks):
        ordered_payload += received[i]

    # Decode reconstructed Base32
    message = decode_base32(ordered_payload)

    return {
        "status": "COMPLETE",
        "message": message
    }


if __name__ == "__main__":

    message = "hello dns lab"

    encoded = encode_base32(message)

    print("Original :", message)
    print("Encoded  :", encoded)

    decoded = decode_base32(encoded)

    print("Decoded  :", decoded)

    chunks = chunk_payload(encoded, 10)

    print("\nChunks:")

    for i, chunk in enumerate(chunks):
        print(i, "->", chunk)

    session_id = "7f3a"
    total_chunks = len(chunks)

    print("\nProtocol Queries:")

    for sequence, chunk in enumerate(chunks):

        query_name = build_query_name(
            session_id,
            sequence,
            total_chunks,
            chunk,
            "tunnel.test"
        )

        print(query_name)

    print("\nParser Test:")

    query = "v1.7f3a.0001.0003.SG44ZANRQW.tunnel.test"

    parsed = parse_query_name(query)

    print(parsed)

    print("\nValidation Tests:")

    test_queries = [
        "v1.7f3a.0001.0003.SG44ZANRQW.tunnel.test",
        "v2.7f3a.0001.0003.SG44ZANRQW.tunnel.test",
        "v1.7f3a.0001.0003.SG44ZANRQW.example.com",
        "v1.7f3a.0003.0003.SG44ZANRQW.tunnel.test",
        "v1.7f3a.0001.0003.INVALID!.tunnel.test"
    ]

    for query in test_queries:

        try:
            result = parse_query_name(query)
            print("VALID  :", query)

        except ValueError as error:
            print("INVALID:", query)
            print("        Reason:", error)

    print("\nReassembly Test:")

    test_chunks = [
        (2, "E"),
        (0, "NBSWY3DPEB"),
        (1, "SG44ZANRQW"),
        (1, "SG44ZANRQW")
    ]

    result = reassemble_chunks(test_chunks, 3)

    print(result)