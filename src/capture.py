import sys

from scapy.all import sniff, DNS, DNSQR, wrpcap


captured_queries = []


def handle_packet(packet):
    if packet.haslayer(DNS) and packet.haslayer(DNSQR) and packet[DNS].qr == 0:
        query_name = packet[DNSQR].qname.decode(errors="ignore")
        print("DNS Query:", query_name)
        captured_queries.append(packet)


output_file = "data/normal_dns.pcap"

if len(sys.argv) > 1:
    output_file = sys.argv[1]


print("DNS Packet Capture Started")
print("Capturing DNS queries on UDP/5353 for 60 seconds...")

sniff(
    iface=r"\Device\NPF_Loopback",
    filter="udp port 5353",
    prn=handle_packet,
    store=False,
    timeout=400
)

wrpcap(output_file, captured_queries)

print("\nCapture complete.")
print("DNS queries captured:", len(captured_queries))
print("PCAP saved to:", output_file)