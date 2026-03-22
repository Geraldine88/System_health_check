import streamlit as st
import random
import time
import pandas as pd
import numpy as np
from datetime import datetime

from pyarrow import timestamp

# -------------------------------------------------------------------------------

# PASTEL THEME COLORS

# -------------------------------------------------------------------------------

PASTEL_INFO = "#A8E6CF"      # mint
PASTEL_WARN = "#FFD3B6"      # peach
PASTEL_ERROR = "#FFAAA5"     # soft red
PASTEL_CPU = "#A0C4FF"       # sky blue
PASTEL_RAM = "#BDB2FF"       # lavender
PASTEL_DISK = "#9BF6FF"      # teal

# -------------------------------------------------------------------------------

# PAGE CONFIGURATIONS

# -------------------------------------------------------------------------------

st.set_page_config(
    page_title="Log Watcher Real-time Dashboard",
    layout="wide",
)
st.title("Log Watcher Real-time Dashboard")
st.caption("Balanced simulation • Soft pastel theme • Auto-updating every second")

# -------------------------------------------------------------------------------

# SESSION STATE INITIALIZATION

# -------------------------------------------------------------------------------
if 'logs' not in st.session_state:
    st.session_state.logs = []

if 'warning_trends' not in st.session_state:
    st.session_state.warning_trends = []

if 'error_trends' not in st.session_state:
    st.session_state.error_trends = []

if 'cpu_trend' not in st.session_state:
    st.session_state.cpu_trend = []

if 'ram_trend' not in st.session_state:
    st.session_state.ram_trend = []

if 'disk_trend' not in st.session_state:
    st.session_state.disk_trend = []

if 'counts' not in st.session_state:
    st.session_state.counts = {"INFO": 0, "WARNING": 0, "ERROR": 0}

# -------------------------------------------------------------------------------

# SIMULATED LOG GENERATOR (BALANCED)

# -------------------------------------------------------------------------------

def generate_log():
    cpu = round(random.uniform(20, 80), 1)
    ram = round(random.uniform(30, 90), 1)
    disk = round(random.uniform(20, 60), 1)

    #Balanced probs
    level = random.choices(
        ['INFO', 'WARNING', 'ERROR'],
        weights=[80, 15, 5],
        k=1
    )[0]

    msg = f"CPU {cpu}%, RAM {ram}%, Disk {disk}%, Level {level}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return timestamp, level, msg, cpu, ram, disk

# -------------------------------------------------------------------------------

# NEW LOG ENTRY GENERATION

# -------------------------------------------------------------------------------

ts, level, msg, cpu, ram, disk = generate_log()

#Updating the counts
st.session_state.counts[level] += 1

# Now, we save the trends
st.session_state.warning_trends.append(st.session_state.counts['WARNING'])
st.session_state.error_trends.append(st.session_state.counts['ERROR'])
st.session_state.cpu_trend.append(cpu)
st.session_state.ram_trend.append(ram)
st.session_state.disk_trend.append(disk)

# Save the logs
st.session_state.logs.append((ts, level, msg))
st.session_state.logs = st.session_state.logs[-50:] # to store last 50 logs

# -------------------------------------------------------------------------------

# METRIC CARD - FIRST SECTION

# -------------------------------------------------------------------------------

st.subheader("System Metrics (Pastel Cards)")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
    f"""<div style="background-color:{PASTEL_INFO}; padding:20px; border-radius:10px;">
                <h3 style="text-align:center;">INFO</h3>
                <h1 style="text-align:center;">{st.session_state.counts['INFO']}</h1>
                </div>
            """,
            unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div style="background-color:{PASTEL_ERROR}; padding:20px; border-radius:10px;">
            <h3 style="text-align:center;">ERROR</h3>
            <h1 style="text-align:center;">{st.session_state.counts['ERROR']}</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# SECTION 3 — LIVE LOG FEED
# ------------------------------------------------------------
st.subheader("Live Log Feed")

log_container = st.container()
with log_container:
    for ts, level, msg in reversed(st.session_state.logs):
        color = (
            PASTEL_INFO if level == "INFO"
            else PASTEL_WARN if level == "WARNING"
            else PASTEL_ERROR
        )
        st.markdown(
            f"""
            <div style="background-color:{color}; padding:10px; border-radius:8px; margin-bottom:5px;">
                <b>{ts}</b> — <b>{level}</b> — {msg}
            </div>
            """,
            unsafe_allow_html=True,
        )

# ------------------------------------------------------------
# Auto-refresh every second
# ------------------------------------------------------------
time.sleep(1)
st.experimental_rerun()
