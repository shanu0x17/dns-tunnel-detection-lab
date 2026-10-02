from scapy.all import sniff, DNSQR, wrpcap

def handle_packet(packet):
    if packet.haslayer(DNSQR):
        query_name = packet[DNSQR].qname.decode(errors="ignore")
        print("DNS Query:", query_name)

print("DNS Tunnel Packet Capture Started")
print("Capturing UDP/5353 traffic for 60 seconds...")

packets = sniff(
    iface=r"\Device\NPF_Loopback",
    filter="udp port 5353",
    prn=handle_packet,
    store=True,
    timeout=60
)

wrpcap("data/dns_tunnel_realistic.pcap", packets)

print("\nCapture complete.")
print("Packets captured:", len(packets))
print("PCAP saved to: data/dns_tunnel_realistic.pcap")