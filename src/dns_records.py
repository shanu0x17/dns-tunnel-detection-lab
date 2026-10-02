import dns.resolver


domain = "example.com"

record_types = [
    "A",
    "AAAA",
    "CNAME",
    "MX",
    "NS",
    "TXT"
]


for record_type in record_types:

    print("\n-------------------------")
    print("Record Type:", record_type)
    print("-------------------------")

    try:

        answer = dns.resolver.resolve(domain, record_type)

        for record in answer:
            print(record)

    except Exception as error:

        print("No record / Query failed")