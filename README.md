# 🛡️ DNS Tunnel Detection Lab

> A controlled cybersecurity research lab for building, observing, and
> detecting DNS tunneling through protocol analysis, traffic capture,
> behavioral feature engineering, and explainable anomaly detection.

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-13%20Passed-brightgreen?logo=pytest)](https://pytest.org/)
\[![Detection](https://img.shields.io/badge/Detection-Explainable-orange)\]
\[![Environment](https://img.shields.io/badge/Environment-Local%20Lab-purple)\]
\[![Status](https://img.shields.io/badge/Status-Complete-success)\]

------------------------------------------------------------------------

## 🚀 Overview

DNS is normally used to resolve domain names, but its flexible query
structure can also carry encoded application data.

This project builds a **controlled DNS tunneling environment** where a
client encodes a harmless message into DNS queries, a local DNS receiver
reconstructs the original message, network traffic is captured,
behavioral features are extracted, and a detector identifies suspicious
DNS activity.

The project combines:

-   🌐 DNS protocol fundamentals
-   🔐 Base32 encoding and payload chunking
-   🐍 Python networking
-   📡 DNS traffic capture and PCAP analysis
-   📊 Behavioral feature engineering
-   🧠 Statistical baseline detection
-   🚨 Explainable anomaly scoring
-   📈 Streamlit visualization
-   🧪 Automated testing
-   🔴 Live DNS monitoring

The focus is on **reproducible defensive analysis**, not
production-grade IDS deployment.

## 🎯 Objectives

1.  Build a controlled DNS tunneling communication channel.
2.  Reconstruct the original message at the controlled DNS receiver.
3.  Capture and analyze normal and tunnel DNS traffic.
4.  Detect suspicious behavior using multiple measurable DNS
    characteristics.
5.  Visualize the evidence through an analyst-oriented dashboard.

## 🧩 Architecture

``` text
DNS Client
   │
   │ Message → Base32 → Chunking
   ▼
Controlled DNS Receiver
   │
   ├── Parse → Validate → Store → Reassemble
   │
   ├──────────────► Reconstructed Message
   │
   ▼
PCAP Capture / Wireshark
   │
   ▼
Feature Extraction
   │
   ├── Entropy
   ├── Label Length
   ├── Query Rate
   ├── Unique Subdomain Ratio
   └── Timing / Burstiness
   │
   ▼
Window-Based Detector
   │
   ├── Normal Baseline
   ├── Multi-Signal Score
   └── Severity
   │
   ├──────────────► Offline Evaluation
   │
   └──────────────► Live Detection
                         │
                         ▼
                 Streamlit Dashboard
```

## 🔐 DNS Tunnel Communication

The communication pipeline is:

``` text
Original Message
      ↓
UTF-8 Bytes
      ↓
Base32 Encoding
      ↓
Payload Chunking
      ↓
DNS Query Construction
      ↓
Controlled DNS Receiver
      ↓
Query Parsing & Validation
      ↓
Chunk Reassembly
      ↓
Original Message
```

### Client → DNS Receiver → Same Message

``` text
CLIENT

Message:
"longer simulated payload for behavioral detection testing"

        ↓

Base32 encoded payload
        ↓
Multiple DNS query chunks
        ↓
Controlled DNS receiver
        ↓

SERVER

Reconstructed message:
"longer simulated payload for behavioral detection testing"
```

This demonstrates that the message transmitted through the controlled
DNS channel can be reconstructed correctly by the receiver.

## 📡 Protocol Format

``` text
v1.<session_id>.<chunk_index>.<total_chunks>.<payload>.tunnel.test
```

Example:

``` text
v1.2008.0000.0010.NRXW4Z3FOI.tunnel.test
```

  Field           Purpose
  --------------- --------------------------
  `v1`            Protocol version
  `2008`          Session identifier
  `0000`          Chunk index
  `0010`          Total chunks
  `NRXW4Z3FOI`    Base32 payload chunk
  `tunnel.test`   Controlled lab namespace

The receiver validates the protocol fields, groups chunks by session,
and reconstructs the payload when the required chunks are available.

## 📊 Detection Methodology

The detector uses a **normal DNS behavioral baseline** and evaluates
traffic in fixed time windows.

  Signal                   What it measures
  ------------------------ ------------------------------------------------
  Shannon entropy          Randomness / character diversity of DNS labels
  Average label length     Length characteristics of queried labels
  Query rate               DNS request frequency
  Unique subdomain ratio   Degree of unique subdomain generation
  Inter-arrival CV         Variation in timing between requests
  Burstiness               Concentration of requests into bursts

> High entropy alone is not treated as proof of tunneling. The detector
> combines multiple behavioral signals.

### Severity

``` text
0 ─────── 30 ─────── 60 ─────── 80 ─────── 100
  LOW       MEDIUM       HIGH       CRITICAL
```

      Score Severity
  --------- ----------
      0--29 LOW
     30--59 MEDIUM
     60--79 HIGH
    80--100 CRITICAL

The score is an **explainable anomaly indicator**, not a definitive
maliciousness verdict.

## 🧪 Controlled Evaluation

The current offline evaluation uses:

  Dataset        Windows
  ------------ ---------
  Normal DNS          34
  DNS Tunnel           3

Observed controlled-lab results:

``` text
True Positives  : 3
True Negatives  : 34
False Positives : 0
False Negatives : 0

Precision : 100%
Recall    : 100%
FPR       : 0%
FNR       : 0%
```

These measurements come from a **small controlled laboratory dataset**
and are not intended to represent production-world detection accuracy.

## 📈 Behavioral Comparison

  Characteristic             Normal DNS   DNS Tunnel
  ------------------------ ------------ ------------
  Query Rate                  1.434 q/s    3.193 q/s
  Unique Subdomain Ratio          0.070        1.000
  Average Inter-arrival       0.699 sec    0.317 sec
  Shannon Entropy                 3.000        3.810

## 🖥️ Dashboard

The dashboard separates two analysis paths.

### Offline Dataset Analysis

Uses stored normal and tunnel datasets for:

-   Dataset overview
-   Normal vs tunnel behavioral comparison
-   Detection results
-   Severity distribution
-   Detection signal contributions
-   Tunnel window/session replay
-   Evaluation results

### Live Monitoring

``` text
Live DNS Traffic
       ↓
10-second Window
       ↓
Feature Extraction
       ↓
Baseline Comparison
       ↓
Detection Score
       ↓
LOW / MEDIUM / HIGH / CRITICAL
       ↓
data/live_windows.csv
       ↓
Dashboard
```

## 📁 Project Structure

``` text
dns-tunnel-lab/
│
├── data/
│   ├── normal_dns.pcap
│   ├── dns_tunnel_realistic.pcap
│   ├── normal_window_features.csv
│   ├── tunnel_window_features.csv
│   └── live_windows.csv
│
├── src/
│   ├── capture.py
│   ├── capture_tunnel.py
│   ├── client.py
│   ├── compare_behavioral.py
│   ├── compare_features.py
│   ├── config.py
│   ├── dashboard.py
│   ├── dns_records.py
│   ├── dns_server.py
│   ├── evaluate_detector.py
│   ├── features.py
│   ├── live_detector.py
│   ├── normal_workload.py
│   ├── pcap_features.py
│   ├── protocol.py
│   ├── tunnel_workload.py
│   ├── window_detector.py
│   └── window_features.py
│
├── tests/
│   ├── test_features.py
│   ├── test_protocol.py
│   └── test_window_detector.py
│
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

## ⚙️ Installation

``` bash
git clone <YOUR_REPOSITORY_URL>
cd dns-tunnel-lab
python -m venv .venv
```

Windows:

``` powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

``` bash
pip install -r requirements.txt
```

## 🧪 Run Tests

``` bash
pytest -q
```

Current result:

``` text
13 passed
```

Tests cover protocol behavior, feature calculations, detector scoring,
score bounds, and severity classification.

## ▶️ Running the Lab

Start the controlled DNS receiver:

``` bash
python src/dns_server.py
```

Generate normal DNS traffic:

``` bash
python src/normal_workload.py
```

Generate controlled tunnel traffic:

``` bash
python src/tunnel_workload.py
```

## 📡 Capture Traffic

Normal traffic:

``` bash
python src/capture.py
```

Tunnel traffic:

``` bash
python src/capture_tunnel.py
```

Captured PCAP files can be inspected using Wireshark.

## 🧮 Generate Window Features

``` bash
python src/window_features.py
```

## 🔍 Evaluate the Detector

``` bash
python src/evaluate_detector.py
```

## 🔴 Run Live Detection

``` bash
python src/live_detector.py
```

Live results are written to:

``` text
data/live_windows.csv
```

## 📊 Launch Dashboard

``` bash
streamlit run src/dashboard.py
```

## 🎬 Recommended Final Demo

``` text
1. Start the controlled DNS receiver
2. Generate ordinary DNS traffic
3. Show normal baseline behavior
4. Send a harmless message through the DNS tunnel
5. Show DNS chunks being received
6. Show the server reconstructing the SAME message
7. Capture the traffic in PCAP
8. Extract behavioral features
9. Run the detector
10. Show the suspicious result
11. Open the dashboard
12. Compare normal vs tunnel behavior
13. Show detection signal contributions
14. Demonstrate live detection
15. Run pytest
```

**Communication → Reconstruction → Capture → Feature Extraction →
Detection → Visualization → Testing**

## 🛠️ Technologies

  Technology    Purpose
  ------------- -----------------------------
  Python 3.13   Core implementation
  dnspython     DNS client/resolution
  dnslib        Controlled DNS server
  Scapy         Packet capture and analysis
  Pandas        Dataset processing
  Altair        Visualization
  Streamlit     Security dashboard
  Pytest        Automated testing
  Wireshark     Manual PCAP inspection

## 🧠 Key Learning Outcomes

-   DNS resolution and query structure
-   UDP-based network communication
-   Base32 encoding and payload chunking
-   Client/server architecture
-   DNS session reconstruction
-   Packet capture and PCAP analysis
-   Behavioral feature engineering
-   Statistical baselines
-   Explainable anomaly detection
-   Security data visualization
-   Automated testing
-   Reproducible security experiments

## ⚠️ Limitations

This is a controlled research and learning environment.

-   Small controlled dataset
-   Local lab environment
-   Limited traffic diversity
-   Statistical detection rather than machine learning
-   Thresholds tuned for the laboratory dataset
-   Legitimate high-entropy DNS traffic may produce anomalies
-   No claim of production-grade detection accuracy

## 🔮 Future Improvements

-   Larger and more diverse DNS datasets
-   Enterprise DNS traffic evaluation
-   Additional temporal features
-   Domain reputation enrichment
-   DNS-over-HTTPS / DNS-over-TLS analysis
-   Machine-learning comparison
-   Streaming packet ingestion
-   SIEM-compatible JSON/CSV alert export
-   Containerized deployment
-   Automated experiment runner

## 🛡️ Responsible Use

This project is intended for **authorized security research, education,
and controlled laboratory environments**.

The DNS communication component exists to demonstrate observable
tunneling behavior so that defensive detection techniques can be
studied.

Do not use the project against networks, domains, systems, or data
without explicit authorization.

## ⭐ Project Summary

DNS Tunnel Detection Lab demonstrates the complete lifecycle of a
controlled DNS tunneling experiment:

``` text
Construct
   ↓
Transmit
   ↓
Reconstruct
   ↓
Capture
   ↓
Extract Features
   ↓
Establish Baseline
   ↓
Detect Anomalies
   ↓
Explain Evidence
   ↓
Visualize Results
```

> **Not just a DNS tunneling script --- a compact cybersecurity research
> and detection lab demonstrating networking, protocol engineering,
> traffic analysis, and security analytics.**
