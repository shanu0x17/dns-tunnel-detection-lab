import csv
import os
import altair as alt
import pandas as pd
import streamlit as st

from window_detector import build_baseline, calculate_window_score, get_status, load_windows

st.set_page_config(page_title="DNS Tunnel Detection Lab", page_icon="🛡️", layout="wide")

NORMAL_BEHAVIOR = "data/normal_behavioral_features.csv"
TUNNEL_BEHAVIOR = "data/tunnel_behavioral_features.csv"
NORMAL_WINDOWS = "data/normal_window_features.csv"
TUNNEL_WINDOWS = "data/tunnel_window_features.csv"
LIVE_FILE = "data/live_windows.csv"

st.markdown("""
<style>
.block-container{padding-top:2rem;padding-bottom:3rem;max-width:1500px}
h1{font-size:2.4rem!important;letter-spacing:-1px}
h2{font-size:1.45rem!important;margin-top:1.5rem!important}
h3{font-size:1.05rem!important}
[data-testid="stMetric"]{background:linear-gradient(145deg,#15171d,#101116);border:1px solid #292c35;border-radius:12px;padding:18px 20px}
[data-testid="stMetricLabel"]{color:#9da3b0}
[data-testid="stMetricValue"]{font-size:1.8rem}
.stTabs [data-baseweb="tab"]{font-weight:600}
.status-live{display:inline-block;padding:5px 12px;border-radius:20px;background:#123522;color:#55d98b;border:1px solid #23643d;font-size:.82rem;font-weight:600}
.status-alert{display:inline-block;padding:5px 12px;border-radius:20px;background:#401b20;color:#ff6977;border:1px solid #7c2933;font-size:.82rem;font-weight:600}
.status-normal{display:inline-block;padding:5px 12px;border-radius:20px;background:#182c43;color:#6faeff;border:1px solid #294b70;font-size:.82rem;font-weight:600}
.panel{background:linear-gradient(145deg,#14161c,#101116);border:1px solid #292c35;border-radius:14px;padding:18px 20px;margin-bottom:14px}
.panel-title{font-size:1.05rem;font-weight:700;margin-bottom:4px}
.panel-sub{color:#858b98;font-size:.86rem}
.alert-box{background:linear-gradient(145deg,#32191d,#211417);border:1px solid #6d2931;border-radius:14px;padding:20px}
.info-box{background:linear-gradient(145deg,#142337,#111923);border:1px solid #24476c;border-radius:14px;padding:20px}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🛡️ DNS Tunnel Detection Lab")
st.markdown("Behavioral and temporal analysis of DNS traffic for controlled tunneling detection.")
st.markdown('<span class="status-live">● LOCAL LAB</span> &nbsp; <span class="status-normal">BASELINE DETECTION</span>', unsafe_allow_html=True)

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
        results.append({"score": round(score, 2), "status": get_status(score), "signals": signals, "row": row})
    return results

def status_counts(results):
    return {level: sum(r["status"] == level for r in results) for level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]}

normal_data = load_csv(NORMAL_BEHAVIOR)
tunnel_data = load_csv(TUNNEL_BEHAVIOR)
normal_windows = load_windows(NORMAL_WINDOWS)
tunnel_windows = load_windows(TUNNEL_WINDOWS)
baseline = build_baseline(normal_windows)
normal_results = score_windows(normal_windows, baseline)
tunnel_results = score_windows(tunnel_windows, baseline)
normal_counts = status_counts(normal_results)
tunnel_counts = status_counts(tunnel_results)

normal_metrics = {
    "Query Rate (q/s)": average(normal_data, "query_rate"),
    "Unique Subdomain Ratio": average(normal_data, "unique_subdomain_ratio"),
    "Average Inter-arrival (sec)": average(normal_data, "average_inter_arrival"),
    "Shannon Entropy": average(normal_data, "shannon_entropy")
}

tunnel_metrics = {
    "Query Rate (q/s)": average(tunnel_data, "query_rate"),
    "Unique Subdomain Ratio": average(tunnel_data, "unique_subdomain_ratio"),
    "Average Inter-arrival (sec)": average(tunnel_data, "average_inter_arrival"),
    "Shannon Entropy": average(tunnel_data, "shannon_entropy")
}

live = pd.read_csv(LIVE_FILE) if os.path.exists(LIVE_FILE) else pd.DataFrame()
latest = live.iloc[-1] if not live.empty else None

if latest is not None:
    live_status = latest["status"]
    live_score = float(latest["score"])
    live_queries = int(latest["query_count"])
    live_rate = float(latest["query_rate"])
else:
    live_status = "IDLE"
    live_score = 0
    live_queries = 0
    live_rate = 0

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["Overview", "Detection Analysis", "Live Monitor"])

with tab1:
    st.subheader("Detection Overview")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Normal Queries", len(normal_data))
    c2.metric("Tunnel Queries", len(tunnel_data))
    c3.metric("Baseline Windows", len(normal_windows))
    c4.metric("Flagged Windows", sum(tunnel_counts[x] for x in ["HIGH", "CRITICAL"]))

    st.markdown("### Traffic Profile")

    profile = pd.DataFrame({
        "Characteristic": ["Query Rate (q/s)", "Unique Subdomain Ratio", "Average Inter-arrival (sec)", "Shannon Entropy"],
        "Normal DNS": [
            normal_metrics["Query Rate (q/s)"],
            normal_metrics["Unique Subdomain Ratio"],
            normal_metrics["Average Inter-arrival (sec)"],
            normal_metrics["Shannon Entropy"]
        ],
        "DNS Tunnel": [
            tunnel_metrics["Query Rate (q/s)"],
            tunnel_metrics["Unique Subdomain Ratio"],
            tunnel_metrics["Average Inter-arrival (sec)"],
            tunnel_metrics["Shannon Entropy"]
        ]
    })

    st.dataframe(
        profile.style.format({"Normal DNS": "{:.3f}", "DNS Tunnel": "{:.3f}"}),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### Detection Distribution")

    severity_data = []
    for name, counts in [("Normal DNS", normal_counts), ("DNS Tunnel", tunnel_counts)]:
        for level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            severity_data.append({"Traffic": name, "Severity": level, "Windows": counts[level]})

    severity_df = pd.DataFrame(severity_data)

    chart = (
        alt.Chart(severity_df)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("Traffic:N", title=None),
            y=alt.Y("Windows:Q", title="Detection Windows"),
            xOffset="Severity:N",
            color=alt.Color(
                "Severity:N",
                scale=alt.Scale(
                    domain=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                    range=["#4C9BE8", "#E7B64A", "#E47C42", "#D43D52"]
                ),
                legend=alt.Legend(title="Severity")
            ),
            tooltip=["Traffic", "Severity", "Windows"]
        )
        .properties(height=360)
    )

    st.altair_chart(chart, use_container_width=True)

    st.markdown("### Current Detection State")

    if latest is not None:
        if live_status in ["HIGH", "CRITICAL"]:
            st.markdown(
                f'<div class="alert-box"><div class="panel-title">Suspicious DNS activity detected</div>'
                f'<div class="panel-sub">Latest live window scored <b>{live_score:.2f}</b> and was classified as '
                f'<b>{live_status}</b>.</div></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="info-box"><div class="panel-title">No high-severity live activity</div>'
                f'<div class="panel-sub">Latest live window scored <b>{live_score:.2f}</b> and was classified as '
                f'<b>{live_status}</b>.</div></div>',
                unsafe_allow_html=True
            )
    else:
        st.info("No live detection window has been recorded yet.")

with tab2:
    st.subheader("Detection Analysis")

    flagged = [
        {"Window": i + 1, "Score": result["score"], "Status": result["status"]}
        for i, result in enumerate(tunnel_results)
        if result["status"] in ["MEDIUM", "HIGH", "CRITICAL"]
    ]

    if flagged:
        st.markdown("### Flagged Tunnel Windows")
        st.dataframe(pd.DataFrame(flagged), use_container_width=True, hide_index=True)
    else:
        st.success("No suspicious tunnel windows were flagged.")

    st.markdown("### Detection Window Replay")

    if tunnel_results:
        selected = st.selectbox("Select detection window", range(1, len(tunnel_results) + 1))
        result = tunnel_results[selected - 1]
        row = result["row"]

        c1, c2, c3 = st.columns(3)
        c1.metric("Window", selected)
        c2.metric("Detection Score", f"{result['score']:.2f}")
        c3.metric("Classification", result["status"])

        feature_names = [
            "average_entropy",
            "average_label_length",
            "query_rate",
            "unique_subdomain_ratio",
            "inter_arrival_cv",
            "burstiness"
        ]

        feature_table = pd.DataFrame({
            "Feature": feature_names,
            "Value": [row.get(x, "N/A") for x in feature_names]
        })

        st.dataframe(feature_table, use_container_width=True, hide_index=True)

    st.markdown("### Detection Signal Contributions")

    signal_totals = {}
    for result in tunnel_results:
        for signal, value in result["signals"].items():
            signal_totals[signal] = signal_totals.get(signal, 0) + value

    if tunnel_results:
        signal_data = pd.DataFrame({
            "Signal": list(signal_totals.keys()),
            "Average Contribution": [
                round(value / len(tunnel_results), 2)
                for value in signal_totals.values()
            ]
        })

        signal_chart = (
            alt.Chart(signal_data)
            .mark_bar(cornerRadiusEnd=5)
            .encode(
                x=alt.X("Average Contribution:Q", title="Average Score Contribution"),
                y=alt.Y("Signal:N", sort="-x", title=None),
                tooltip=["Signal", "Average Contribution"]
            )
            .properties(height=300)
        )

        st.altair_chart(signal_chart, use_container_width=True)

    st.markdown("### Detection Assessment")

    high_count = tunnel_counts["HIGH"] + tunnel_counts["CRITICAL"]

    if high_count:
        st.markdown(
            f'<div class="alert-box"><div class="panel-title">{high_count} high-severity tunnel windows detected</div>'
            f'<div class="panel-sub">The detector combines entropy, label length, query rate, subdomain uniqueness '
            f'and timing behavior to produce the window score.</div></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="info-box"><div class="panel-title">No high-severity tunnel windows detected</div>'
            '<div class="panel-sub">Observed windows remained below the HIGH severity threshold.</div></div>',
            unsafe_allow_html=True
        )

with tab3:
    st.subheader("Live DNS Monitor")

    if latest is None:
        st.info("Live detector is not running or no live data has been recorded yet.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Queries", live_queries)
        c2.metric("Query Rate", f"{live_rate:.2f} q/s")
        c3.metric("Detection Score", f"{live_score:.2f}")

        if live_status == "CRITICAL":
            c4.error("🔴 CRITICAL")
        elif live_status == "HIGH":
            c4.warning("🟠 HIGH")
        elif live_status == "MEDIUM":
            c4.info("🟡 MEDIUM")
        else:
            c4.success("🔵 LOW")

        st.markdown("### Detection Score Timeline")

        score_data = live[["timestamp", "score"]].copy()
        score_data["timestamp"] = pd.to_datetime(score_data["timestamp"])

        timeline = (
            alt.Chart(score_data)
            .mark_line(point=True, strokeWidth=3)
            .encode(
                x=alt.X("timestamp:T", title="Time"),
                y=alt.Y("score:Q", title="Detection Score", scale=alt.Scale(domain=[0, 100])),
                tooltip=["timestamp:T", "score:Q"]
            )
            .properties(height=380)
        )

        st.altair_chart(timeline, use_container_width=True)

        st.markdown("### Recent Detection Windows")

        columns = [
            "timestamp",
            "query_count",
            "query_rate",
            "average_entropy",
            "unique_subdomain_ratio",
            "score",
            "status"
        ]

        available_columns = [x for x in columns if x in live.columns]

        st.dataframe(
            live.tail(10)[available_columns],
            use_container_width=True,
            hide_index=True
        )

        st.markdown("### Latest Window Signals")

        signal_columns = [
            "average_entropy",
            "average_label_length",
            "query_rate",
            "unique_subdomain_ratio",
            "inter_arrival_cv",
            "burstiness"
        ]

        live_signal_data = pd.DataFrame({
            "Signal": [x.replace("_", " ").title() for x in signal_columns if x in live.columns],
            "Value": [latest[x] for x in signal_columns if x in live.columns]
        })

        st.dataframe(live_signal_data, use_container_width=True, hide_index=True)