from protocol import (
    encode_base32,
    decode_base32,
    chunk_payload,
    build_query_name,
    parse_query_name,
    reassemble_chunks
)


def test_base32_round_trip():
    message = "hello dns lab"

    encoded = encode_base32(message)
    decoded = decode_base32(encoded)

    assert decoded == message

def test_chunk_payload():
    data = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    chunks = chunk_payload(data, 10)

    assert chunks == [
        "ABCDEFGHIJ",
        "KLMNOPQRST",
        "UVWXYZ"
    ]

def test_build_query_name():
    query = build_query_name(
        "7f3a",
        1,
        3,
        "SG44ZANRQW",
        "tunnel.test"
    )

    assert query == (
        "v1.7f3a.0001.0003.SG44ZANRQW.tunnel.test"
    )
    
def test_parse_query_name():
    query = "v1.7f3a.0001.0003.SG44ZANRQW.tunnel.test"

    result = parse_query_name(query)

    assert result["version"] == "v1"
    assert result["session_id"] == "7f3a"
    assert result["sequence"] == 1
    assert result["total_chunks"] == 3
    assert result["payload"] == "SG44ZANRQW"
    assert result["lab_domain"] == "tunnel.test"

def test_reassembly_with_reordered_chunks():
    chunks = [
        (2, "E"),
        (0, "NBSWY3DPEB"),
        (1, "SG44ZANRQW")
    ]

    result = reassemble_chunks(chunks, 3)

    assert result["status"] == "COMPLETE"
    assert result["message"] == "hello dns lab"

def test_reassembly_duplicate():
    chunks = [
        (0, "NBSWY3DPEB"),
        (1, "SG44ZANRQW"),
        (1, "SG44ZANRQW"),
        (2, "E")
    ]

    result = reassemble_chunks(chunks, 3)

    assert result["status"] == "COMPLETE"
    assert result["message"] == "hello dns lab"

def test_reassembly_missing_chunk():
    chunks = [
        (0, "NBSWY3DPEB"),
        (2, "E")
    ]

    result = reassemble_chunks(chunks, 3)

    assert result["status"] == "INCOMPLETE"
    assert result["missing_sequences"] == [1]

def test_invalid_namespace():
    query = "v1.7f3a.0001.0003.SG44ZANRQW.example.com"

    try:
        parse_query_name(query)
        assert False
    except ValueError:
        assert True