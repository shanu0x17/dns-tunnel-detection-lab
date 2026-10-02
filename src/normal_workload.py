import random
import time

import dns.resolver


domains = [
    "example.com", "google.com", "youtube.com", "github.com",
    "microsoft.com", "wikipedia.org", "python.org", "mozilla.org",
    "ubuntu.com", "debian.org", "stackoverflow.com", "npmjs.com",
    "pypi.org", "cloudflare.com", "w3.org", "ietf.org",
    "mit.edu", "stanford.edu", "kernel.org", "apache.org",
    "nginx.org", "docker.com", "kubernetes.io", "reddit.com",
    "linkedin.com", "gitlab.com", "oracle.com", "ibm.com",
    "adobe.com", "intel.com", "amd.com", "nvidia.com",
    "zoom.us", "slack.com", "discord.com"
]


resolver = dns.resolver.Resolver(configure=False)
resolver.nameservers = ["127.0.0.1"]
resolver.port = 5353


QUERY_COUNT = 500

print("Normal DNS workload started.")
print("Queries:", QUERY_COUNT)

for i in range(QUERY_COUNT):

    domain = random.choice(domains)

    try:
        resolver.resolve(domain, "A")
        print(f"{i + 1}: {domain}")

    except Exception:
        print(f"{i + 1}: {domain} (server response handled)")

    time.sleep(random.uniform(0.2, 1.2))


print("\nNormal DNS workload complete.")