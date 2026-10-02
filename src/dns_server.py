from dnslib import DNSRecord, RR, A
from dnslib.server import BaseResolver, DNSServer

from src.protocol import parse_query_name, reassemble_chunks 


class LabResolver(BaseResolver):
    
    def __init__(self):
        self.sessions = {}

    def resolve(self, request, handler):

        qname = str(request.q.qname).rstrip(".")

        print("\nDNS Query Received:")
        print("Query Name:", qname)

        try:
            parsed = parse_query_name(qname)

            print("Parsed Query:")
            print(parsed)

            session_id = parsed["session_id"]
            sequence = parsed["sequence"]
            total_chunks = parsed["total_chunks"]
            payload = parsed["payload"]

    # Create storage for a new session
            if session_id not in self.sessions:
             self.sessions[session_id] = {}

    # Store the chunk
            if sequence in self.sessions[session_id]:

                print("Duplicate chunk ignored:", sequence)

            else:

                 self.sessions[session_id][sequence] = payload

            print("Stored Chunks:")
            print(self.sessions[session_id])
            
            if len(self.sessions[session_id]) == total_chunks:

                print("\nAll chunks received!")

                stored_chunks = []

                for seq in sorted(self.sessions[session_id]):
                    chunk = self.sessions[session_id][seq]
                    stored_chunks.append((seq, chunk))

                print("Chunks for reassembly:")
                print(stored_chunks)

                result = reassemble_chunks(
                stored_chunks,
                total_chunks)
            

                print("Reassembly Result:")
                print(result)
            else:

                received = self.sessions[session_id]

                missing_sequences = [
                seq
                for seq in range(total_chunks)
                if seq not in received
                ]

                print("\nSession incomplete!")

                print("Received:", len(received), "/", total_chunks)

                print("Missing sequences:", missing_sequences)

        except ValueError as error:

            print("Invalid Query:")
            print("Reason:", error)
    
        reply = request.reply()

        reply.add_answer(
        RR(
            qname,
            rdata=A("127.0.0.1"),
            ttl=60
        )
    )

        return reply


resolver = LabResolver()

server = DNSServer(
    resolver,
    port=5353,
    address="127.0.0.1"
)

print("DNS Lab Receiver started")
print("Listening on 127.0.0.1:5353")

server.start()