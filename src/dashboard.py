import csv
import os

import altair as alt
import pandas as pd
import streamlit as st

from window_detector import (
    build_baseline,
    calculate_window_score,
    get_status,
    load_windows,
)


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="DNS Tunnel Detection Lab",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ DNS Tunnel Detection Lab")
st.caption(
    "Explainable DNS tunneling detection using behavioral "
    "and temporal DNS characteristics."
)


# ============================================================
# FILES
# ============================================================

NORMAL_BEHAVIOR = "data/normal_behavioral_features.csv"
TUNNEL_BEHAVIOR = "data/tunnel_behavioral_features.csv"
NORMAL_WINDOWS = "data/normal_window_features.csv"
TUNNEL_WINDOWS = "data/tunnel_window_features.csv"
LIVE_FILE = "data/live_windows.csv"


# ============================================================
# HELPERS
# ============================================================

def load_csv(filename):
    if not os.path.exists(filename):
        st.error(f"Dataset not found: {filename}")
        st.stop()

    with open(filename, newline="") as f:
        return list(csv.DictReader(f))


def average(data, field):
    values = []

    for row in data:
        try:
            values.append(float(row[field]))
        except (KeyError, ValueError, TypeError):
            pass

    return sum(values) / len(values) if values else 0


def score_windows(data, baseline):
    results = []

    for row in data:
        score, signals = calculate_window_score(row, baseline)
        results.append({
            "score": round(score, 2),
            "status": get_status(score),
            "signals": signals,
            "row": row
        })

    return results


def status_counts(results):
    return {
        "LOW": sum(r["status"] == "LOW" for r in results),
        "MEDIUM": sum(r["status"] == "MEDIUM" for r in results),
        "HIGH": sum(r["status"] == "HIGH" for r in results),
        "CRITICAL": sum(r["status"] == "CRITICAL" for r in results)
    }


# ============================================================
# LOAD DATA
# ============================================================

normal_data = load_csv(NORMAL_BEHAVIOR)
tunnel_data = load_csv(TUNNEL_BEHAVIOR)

normal_windows = load_windows(NORMAL_WINDOWS)
tunnel_windows = load_windows(TUNNEL_WINDOWS)

baseline = build_baseline(normal_windows)

normal_results = score_windows(normal_windows, baseline)
tunnel_results = score_windows(tunnel_windows, baseline)

normal_counts = status_counts(normal_results)
tunnel_counts = status_counts(tunnel_results)


# ============================================================
# DATASET OVERVIEW
# ============================================================

st.header("📦 Dataset Overview")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Normal Queries", len(normal_data))

with c2:
    st.metric("Tunnel Queries", len(tunnel_data))

with c3:
    st.metric("Normal Windows", len(normal_windows))

with c4:
    st.metric("Tunnel Windows", len(tunnel_windows))


# ============================================================
# BEHAVIORAL COMPARISON
# ============================================================

st.header("📊 Behavioral Comparison")
st.caption("Average characteristics of normal and tunnel DNS traffic.")

normal_metrics = {
    "Query Rate (q/s)": average(normal_data, "query_rate"),
    "Unique Subdomain Ratio": average(
        normal_data, "unique_subdomain_ratio"
    ),
    "Average Inter-arrival (sec)": average(
        normal_data, "average_inter_arrival"
    ),
    "Shannon Entropy": average(
        normal_data, "shannon_entropy"
    ),
}

tunnel_metrics = {
    "Query Rate (q/s)": average(tunnel_data, "query_rate"),
    "Unique Subdomain Ratio": average(
        tunnel_data, "unique_subdomain_ratio"
    ),
    "Average Inter-arrival (sec)": average(
        tunnel_data, "average_inter_arrival"
    ),
    "Shannon Entropy": average(
        tunnel_data, "shannon_entropy"
    ),
}

comparison = pd.DataFrame({
    "Characteristic": list(normal_metrics.keys()),
    "Normal DNS": list(normal_metrics.values()),
    "DNS Tunnel": list(tunnel_metrics.values())
})

st.dataframe(
    comparison.style.format({
        "Normal DNS": "{:.3f}",
        "DNS Tunnel": "{:.3f}"
    }),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DETECTION SUMMARY
# ============================================================

st.header("🎯 Detection Summary")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Normal Avg. Entropy",
        f"{normal_metrics['Shannon Entropy']:.2f}"
    )

with c2:
    st.metric(
        "Tunnel Avg. Entropy",
        f"{tunnel_metrics['Shannon Entropy']:.2f}"
    )

with c3:
    st.metric(
        "Normal Avg. Query Rate",
        f"{normal_metrics['Query Rate (q/s)']:.2f}"
    )

with c4:
    st.metric(
        "Tunnel Avg. Query Rate",
        f"{tunnel_metrics['Query Rate (q/s)']:.2f}"
    )


# ============================================================
# DETECTION RESULTS
# ============================================================

st.header("🚦 Detection Results")

c1, c2 = st.columns(2)

with c1:
    st.subheader("Normal DNS")
    st.write(f"🔵 LOW: {normal_counts['LOW']}")
    st.write(f"🟡 MEDIUM: {normal_counts['MEDIUM']}")
    st.write(f"🟠 HIGH: {normal_counts['HIGH']}")
    st.write(f"🔴 CRITICAL: {normal_counts['CRITICAL']}")

with c2:
    st.subheader("DNS Tunnel")
    st.write(f"🔵 LOW: {tunnel_counts['LOW']}")
    st.write(f"🟡 MEDIUM: {tunnel_counts['MEDIUM']}")
    st.write(f"🟠 HIGH: {tunnel_counts['HIGH']}")
    st.write(f"🔴 CRITICAL: {tunnel_counts['CRITICAL']}")


# ============================================================
# SEVERITY DISTRIBUTION
# ============================================================

st.header("📈 Severity Distribution")

severity_data = []

for name, counts in [
    ("Normal DNS", normal_counts),
    ("DNS Tunnel", tunnel_counts)
]:
    for level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
        severity_data.append({
            "Dataset": name,
            "Severity": level,
            "Count": counts[level]
        })

severity_df = pd.DataFrame(severity_data)

chart = (
    alt.Chart(severity_df)
    .mark_bar()
    .encode(
        x=alt.X("Dataset:N", title="Traffic Type"),
        y=alt.Y("Count:Q", title="Windows"),
        xOffset="Severity:N",
        color=alt.Color(
            "Severity:N",
            scale=alt.Scale(
                domain=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                range=["#6BAED6", "#F4B183", "#E67E22", "#8B0000"]
            )
        ),
        tooltip=["Dataset", "Severity", "Count"]
    )
    .properties(height=350)
)

st.altair_chart(chart, use_container_width=True)


# ============================================================
# FLAGGED WINDOWS
# ============================================================

st.header("🚨 Flagged DNS Windows")

flagged = []

for i, result in enumerate(tunnel_results):
    if result["status"] in ["MEDIUM", "HIGH", "CRITICAL"]:
        flagged.append({
            "Window": i + 1,
            "Score": result["score"],
            "Status": result["status"]
        })

if flagged:
    st.dataframe(
        flagged,
        use_container_width=True,
        hide_index=True
    )
else:
    st.success("No suspicious tunnel windows were flagged.")


# ============================================================
# WINDOW REPLAY
# ============================================================

st.header("🔴 Attack Replay")
st.caption("Inspect individual tunnel detection windows.")

if tunnel_results:
    selected = st.selectbox(
        "Select Tunnel Window",
        range(1, len(tunnel_results) + 1)
    )

    result = tunnel_results[selected - 1]
    row = result["row"]

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Window", selected)

    with c2:
        st.metric("Score", f"{result['score']:.2f}")

    with c3:
        st.metric("Status", result["status"])

    st.subheader("Window Features")

    feature_names = [
        "average_entropy",
        "average_label_length",
        "query_rate",
        "unique_subdomain_ratio",
        "inter_arrival_cv",
        "burstiness"
    ]

    feature_table = {
        key: row.get(key, "N/A")
        for key in feature_names
    }

    st.dataframe(
        pd.DataFrame(
            list(feature_table.items()),
            columns=["Feature", "Value"]
        ),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# SIGNAL CONTRIBUTIONS
# ============================================================

st.header("🔎 Detection Signal Contributions")

signal_totals = {}

for result in tunnel_results:
    for signal, value in result["signals"].items():
        signal_totals[signal] = (
            signal_totals.get(signal, 0) + value
        )

if tunnel_results:
    signal_data = pd.DataFrame({
        "Signal": list(signal_totals.keys()),
        "Average Contribution": [
            round(v / len(tunnel_results), 2)
            for v in signal_totals.values()
        ]
    })

    chart = (
        alt.Chart(signal_data)
        .mark_bar()
        .encode(
            x=alt.X(
                "Average Contribution:Q",
                title="Average Score Contribution"
            ),
            y=alt.Y(
                "Signal:N",
                sort="-x",
                title="Detection Signal"
            ),
            tooltip=["Signal", "Average Contribution"]
        )
        .properties(height=350)
    )

    st.altair_chart(chart, use_container_width=True)


# ============================================================
# TOP SUSPICIOUS WINDOWS
# ============================================================

st.header("🚨 Top Suspicious Windows")

top_windows = []

for i, result in enumerate(tunnel_results):
    top_windows.append({
        "Window": i + 1,
        "Score": result["score"],
        "Status": result["status"]
    })

top_windows.sort(
    key=lambda x: x["Score"],
    reverse=True
)

st.dataframe(
    top_windows[:10],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# ANALYST SUMMARY
# ============================================================

st.header("🧠 Analyst Summary")

high_count = (
    tunnel_counts["HIGH"]
    + tunnel_counts["CRITICAL"]
)

if high_count:
    st.warning(
        f"Detected {high_count} HIGH/CRITICAL "
        f"tunnel windows."
    )
else:
    st.success("No HIGH or CRITICAL tunnel windows detected.")

st.info(
    "Detection combines entropy, label length, query rate, "
    "subdomain uniqueness and timing behavior."
)


# ============================================================
# LIVE MONITOR
# ============================================================

st.header("🟢 Live DNS Monitor")
st.caption("Detection windows generated by the live detector.")

if os.path.exists(LIVE_FILE):

    live = pd.read_csv(LIVE_FILE)

    if not live.empty:

        latest = live.iloc[-1]

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric("Queries", int(latest["query_count"]))

        with c2:
            st.metric(
                "Query Rate",
                f"{latest['query_rate']:.2f} q/s"
            )

        with c3:
            st.metric(
                "Detection Score",
                f"{latest['score']:.2f}"
            )

        with c4:
            status = latest["status"]

            if status == "CRITICAL":
                st.error(f"🔴 {status}")
            elif status == "HIGH":
                st.warning(f"🟠 {status}")
            elif status == "MEDIUM":
                st.info(f"🟡 {status}")
            else:
                st.success(f"🔵 {status}")

        st.subheader("Detection Score Timeline")

        score_data = live[["timestamp", "score"]].copy()
        score_data["timestamp"] = pd.to_datetime(
            score_data["timestamp"]
        )

        st.line_chart(
            score_data.set_index("timestamp")
        )

        st.subheader("Recent Detection Windows")

        columns = [
            "timestamp",
            "query_count",
            "query_rate",
            "average_entropy",
            "unique_subdomain_ratio",
            "score",
            "status"
        ]

        st.dataframe(
            live.tail(10)[columns],
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("Live detector has not generated any windows yet.")

else:
    st.info(
        "Live detector is not running or no live data "
        "has been recorded yet."
    )