import streamlit as st
import random
import time
import pandas as pd
from datetime import datetime
from utils.parser import parse_log, extract_metrics

LOG_PATH = "system-health-checker/logs/sys-health-checker.log"

# -------------------------------------------------------------------------------
# BACKGROUND IMAGE (white + lavender theme overlay)
# -------------------------------------------------------------------------------

st.markdown(
    """
    <style>

    /* -----------------------------------------------------------
       IMPORT GOOGLE FONTS
    ----------------------------------------------------------- */
    @import url('https://fonts.googleapis.com/css2?family=Bitcount+Grid+Double+Ink:wght@100..900&family=Caveat:wght@400..700&display=swap');


    /* -----------------------------------------------------------
       BACKGROUND IMAGE + LAVENDER GRADIENT (visible)
    ----------------------------------------------------------- */
    .stApp {
        background:
            linear-gradient(
                rgba(255, 255, 255, 0.15),
                rgba(189, 178, 255, 0.15)
            ),
            url("assets/img.png");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }


    /* -----------------------------------------------------------
       TITLE — BOLD + CAPS + CENTERED (NO GLOW)
    ----------------------------------------------------------- */
    html, body, [class*="st-emotion-cache"] h1 {
        font-family: 'Bitcount Grid Double Ink', sans-serif !important;
        text-align: center !important;
        color: #3A2E6E !important;

        font-weight: 900 !important;   /* BOLD */
        text-transform: uppercase !important;  /* ALL CAPS */

        padding-bottom: 8px;
        width: fit-content;
        margin-left: auto;
        margin-right: auto;

        animation: fadeInTitle 1.2s ease-in-out;
    }

    @keyframes fadeInTitle {
        from { opacity: 0; transform: translateY(-10px); }
        to   { opacity: 1; transform: translateY(0px); }
    }


    /* -----------------------------------------------------------
       SUBHEADERS — MATCH TITLE FONT
    ----------------------------------------------------------- */
    h2, h3, h4 {
        color: #3A2E6E !important;
        font-family: 'Bitcount Grid Double Ink', sans-serif !important;
    }


    /* -----------------------------------------------------------
       FROSTED GLASS CARDS
    ----------------------------------------------------------- */
    .overlay {
        background: rgba(255, 255, 255, 0.35);
        padding: 20px;
        border-radius: 16px;
        color: #3A2E6E;

        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);

        border: 1px solid rgba(255, 255, 255, 0.4);

        animation: fadeInCard 0.8s ease-in-out;
    }

    @keyframes fadeInCard {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0px); }
    }


    /* -----------------------------------------------------------
       LOG TEXT — HANDWRITTEN FONT
    ----------------------------------------------------------- */
    .log-entry {
        color: #3A2E6E;
        font-family: 'Caveat', cursive;
        font-size: 1.2rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)
# -------------------------------------------------------------------------------
# PASTEL THEME COLORS (updated to white + lavender)
# -------------------------------------------------------------------------------

PASTEL_INFO = "#FFFFFF"       # white
PASTEL_WARN = "#E8D7FF"       # soft lavender
PASTEL_ERROR = "#FFB3C6"      # soft rose red
PASTEL_CPU = "#C8B6FF"        # lavender
PASTEL_RAM = "#EDE7FF"        # lilac
PASTEL_DISK = "#D0BCFF"       # muted lavender

# -------------------------------------------------------------------------------
# PAGE CONFIGURATIONS
# -------------------------------------------------------------------------------

st.set_page_config(
    page_title="Log Watcher Real-time Dashboard",
    layout="wide",
)

st.title("Log Watcher Real-time Dashboard")
st.caption("White + Lavender Theme --> Pause | Resume | Single Refresh")

# -------------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------------------------------------------------------

if "logs" not in st.session_state:
    st.session_state.logs = []

if "warning_trends" not in st.session_state:
    st.session_state.warning_trends = []

if "error_trends" not in st.session_state:
    st.session_state.error_trends = []

if "cpu_trend" not in st.session_state:
    st.session_state.cpu_trend = []

if "ram_trend" not in st.session_state:
    st.session_state.ram_trend = []

if "disk_trend" not in st.session_state:
    st.session_state.disk_trend = []

if "counts" not in st.session_state:
    st.session_state.counts = {"INFO": 0, "WARNING": 0, "ERROR": 0}

if "run_mode" not in st.session_state:
    st.session_state.run_mode = "running"   # running | paused | single

# -------------------------------------------------------------------------------
# SIMULATED LOG GENERATOR (BALANCED)
# -------------------------------------------------------------------------------

def generate_log():
    cpu = round(random.uniform(20, 80), 1)
    ram = round(random.uniform(30, 90), 1)
    disk = round(random.uniform(20, 60), 1)

    level = random.choices(
        ["INFO", "WARNING", "ERROR"],
        weights=[80, 15, 5],
        k=1
    )[0]

    msg = f"CPU {cpu}%, RAM {ram}%, Disk {disk}%, Level {level}"
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return ts, level, msg, cpu, ram, disk

# -------------------------------------------------------------------------------
# REAL LOG READER
# -------------------------------------------------------------------------------
def read_new_log_lines():
    log_path = LOG_PATH

    if "log_position" not in st.session_state:
        st.session_state.log_position = 0

    with open(log_path, "r") as f:
        f.seek(st.session_state.log_position)
        lines = f.readlines()
        st.session_state.log_position = f.tell()

    return lines


# -------------------------------------------------------------------------------
# CONTROL BUTTONS (Pause, Resume, One-time Refresh)
# -------------------------------------------------------------------------------

colA, colB, colC = st.columns(3)

with colA:
    if st.button("⏸️ Pause"):
        st.session_state.run_mode = "paused"

with colB:
    if st.button("▶️ Resume"):
        st.session_state.run_mode = "running"

with colC:
    if st.button("🔄 One-time Refresh"):
        st.session_state.run_mode = "single"

# -------------------------------------------------------------------------------
# AUTO-REFRESH LOOP (Cloud-safe using st.empty)
# -------------------------------------------------------------------------------

placeholder = st.empty()

while True:
    with placeholder.container():

        # Only generate new data if running or single refresh
        if st.session_state.run_mode in ["running", "single"]:
            # ts, level, msg, cpu, ram, disk = generate_log()
            lines = read_new_log_lines()

            for line in lines:

                if not line or not line.strip():
                    continue

                parsed = parse_log(line)
                if not parsed:
                    continue

                ts, level, msg = parsed

                try:
                    cpu, ram, disk = extract_metrics(msg)
                except:
                    continue

                st.session_state.counts[level] += 1
                st.session_state.warning_trends.append(st.session_state.counts["WARNING"])
                st.session_state.error_trends.append(st.session_state.counts["ERROR"])
                st.session_state.cpu_trend.append(cpu)
                st.session_state.ram_trend.append(ram)
                st.session_state.disk_trend.append(disk)
                st.session_state.logs.append((ts, level, msg))
                st.session_state.logs = st.session_state.logs[-50:]

        # If single refresh, switch back to paused
        if st.session_state.run_mode == "single":
            st.session_state.run_mode = "paused"

        # -----------------------------------------------------------------------
        # METRIC CARDS
        # -----------------------------------------------------------------------

        st.subheader("System Metrics")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f"""
                <div class="overlay" style="background-color:{PASTEL_INFO};">
                    <h3 style="text-align:center;">INFO</h3>
                    <h1 style="text-align:center;">{st.session_state.counts['INFO']}</h1>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
                <div class="overlay" style="background-color:{PASTEL_WARN};">
                    <h3 style="text-align:center;">WARNING</h3>
                    <h1 style="text-align:center;">{st.session_state.counts['WARNING']}</h1>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                f"""
                <div class="overlay" style="background-color:{PASTEL_ERROR};">
                    <h3 style="text-align:center;">ERROR</h3>
                    <h1 style="text-align:center;">{st.session_state.counts['ERROR']}</h1>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # -----------------------------------------------------------------------
        # REAL-TIME TREND GRAPHS
        # -----------------------------------------------------------------------

        st.subheader("Real-Time Trend Graphs")

        trend_df = pd.DataFrame({
            "Warnings": st.session_state.warning_trends,
            "Errors": st.session_state.error_trends,
            "CPU": st.session_state.cpu_trend,
            "RAM": st.session_state.ram_trend,
            "Disk": st.session_state.disk_trend,
        })

        st.line_chart(trend_df, height=300)

        # -----------------------------------------------------------------------
        # AI-STYLE INSIGHTS
        # -----------------------------------------------------------------------

        st.subheader("AI Insights")


        def generate_insights():
            insights = []

            # CPU Trend
            if len(st.session_state.cpu_trend) > 10:
                if st.session_state.cpu_trend[-1] > st.session_state.cpu_trend[-10]:
                    insights.append("CPU usage is trending upward.")
                else:
                    insights.append("CPU usage is stable or decreasing.")

            # RAM Trend
            if len(st.session_state.ram_trend) > 10:
                if st.session_state.ram_trend[-1] > st.session_state.ram_trend[-10]:
                    insights.append("RAM usage is increasing over time.")
                else:
                    insights.append("RAM usage is stable.")

            # Disk Trend
            if len(st.session_state.disk_trend) > 10:
                if st.session_state.disk_trend[-1] > st.session_state.disk_trend[-10]:
                    insights.append("Disk usage is slowly rising.")
                else:
                    insights.append("Disk usage remains consistent.")

            # Warning Rate
            if len(st.session_state.warning_trends) > 10:
                if st.session_state.warning_trends[-1] > st.session_state.warning_trends[-10]:
                    insights.append("Warning frequency has increased recently.")
                else:
                    insights.append("Warning frequency is stable.")

            # Error Rate
            if len(st.session_state.error_trends) > 10:
                if st.session_state.error_trends[-1] > st.session_state.error_trends[-10]:
                    insights.append("Error rate is rising — monitor closely.")
                else:
                    insights.append("Error rate is stable.")

            return insights


        insights = generate_insights()

        for insight in insights:
            st.markdown(
                f"""
                <div class="overlay" style="margin-bottom: 8px;">
                    <b>• {insight}</b>
                </div>
                """,
                unsafe_allow_html=True
            )

        # -----------------------------------------------------------------------
        # LIVE LOG FEED
        # -----------------------------------------------------------------------

        st.subheader("Live Log Feed")

        for ts, level, msg in reversed(st.session_state.logs):
            color = (
                PASTEL_INFO if level == "INFO"
                else PASTEL_WARN if level == "WARNING"
                else PASTEL_ERROR
            )
            st.markdown(
                f"""
                <div class="overlay" style="background-color:{color}; margin-bottom:5px;">
                    <b>{ts}</b> — <b>{level}</b> — {msg}
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Only auto-refresh if running
    if st.session_state.run_mode == "running":
        time.sleep(1)
    else:
        break