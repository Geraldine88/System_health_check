"""
Real-time log watcher with dashboard, alerting, and graphing.
"""

import argparse
import os
import time
import logging
import re
import matplotlib.pyplot as plt

# ANSI Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

LOG_PATH = "../../system-health-checker/logs/sys-health-checker.log"


# ------------------------------------------------------------
# Parsing
# ------------------------------------------------------------
def parse_log(line):
    try:
        parts = line.split(" - ")
        timestamp = parts[0]
        level = parts[2]
        msg = parts[3].strip()
        return timestamp, level, msg
    except Exception as e:
        logging.error(f"Error parsing log line {line} | Error: {e}")
        return None


def extract_metrics(msg):
    """Extract CPU, RAM, Disk usage from log message."""
    cpu = ram = disk = None
    try:
        cpu_match = re.search(r"CPU Usage (\d+\.?\d*)%", msg)
        ram_match = re.search(r"RAM Usage (\d+\.?\d*)%", msg)
        disk_match = re.search(r"Disk Usage (\d+\.?\d*)%", msg)

        if cpu_match: cpu = float(cpu_match.group(1))
        if ram_match: ram = float(ram_match.group(1))
        if disk_match: disk = float(disk_match.group(1))
    except:
        pass

    return cpu, ram, disk


# ------------------------------------------------------------
# Dashboard + Alerts
# ------------------------------------------------------------
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def render_dashboard(counts, last_events, anomaly=False):
    clear_screen()
    print("======  REAL-TIME LOG DASHBOARD ======")
    print(f"Watching log file:  {LOG_PATH}\n")

    print(f"{GREEN}Info:     {counts['INFO']}{RESET}")
    print(f"{YELLOW}Warnings: {counts['WARNING']}{RESET}")
    print(f"{RED}Errors:   {counts['ERROR']}{RESET}\n")

    print("Last Event:")
    if last_events:
        ts, level, msg = last_events[-1]
        color = GREEN if level == "INFO" else YELLOW if level == "WARNING" else RED
        print(f"{color}[{ts}] {level} - {msg}{RESET}")
    else:
        print("No events to log yet")

    print("\nRecent Events:")
    for ts, level, msg in reversed(last_events):
        short_ts = ts.split(" ")[1] if " " in ts else ts
        color = GREEN if level == "INFO" else YELLOW if level == "WARNING" else RED
        print(f"{color}[{short_ts}] {level:<7} - {msg}{RESET}")

    print("\nAnomaly:", f"{RED}YES{RESET}" if anomaly else f"{GREEN}NO{RESET}")
    print("======================================================================")


def log_alert_to_file(message):
    alerts_dir = "alerts"
    os.makedirs(alerts_dir, exist_ok=True)
    alert_path = os.path.join(alerts_dir, "alerts.log")

    with open(alert_path, "a") as f:
        f.write(message + "\n")


def trigger_alert(level, ts, msg, counts):
    alert_message = None

    if level == "ERROR":
        alert_message = f"ERROR at {ts}: {msg}"
        print(f"\n{RED}🚨 {alert_message}{RESET}")

    elif level == "WARNING" and counts["WARNING"] % 10 == 0:
        alert_message = f"WARNING spike: {counts['WARNING']} warnings so far"
        print(f"\n{YELLOW}⚠️ {alert_message}{RESET}")

    if alert_message:
        log_alert_to_file(alert_message)


# ------------------------------------------------------------
# Graph Saving
# ------------------------------------------------------------
def save_graph(filename):
    graphs_dir = "../graphs"
    os.makedirs(graphs_dir, exist_ok=True)
    path = os.path.join(graphs_dir, filename)
    plt.savefig(path)
    print(f"{GREEN}Saved graph to {path}{RESET}")


# ------------------------------------------------------------
# Graphing Functions
# ------------------------------------------------------------
def plot_warning_trend(timestamps, warning_counts):
    if not timestamps:
        print(f"{YELLOW}No warning data to plot.{RESET}")
        return

    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, warning_counts, marker="o", color="orange", linewidth=2)
    plt.xticks(rotation=45, ha="right")
    plt.title("Warning Trend Over Time")
    plt.xlabel("Timestamp")
    plt.ylabel("Warning Count")
    plt.grid(True)
    plt.tight_layout()
    save_graph("warning_trend.png")
    plt.show(block=True)


def plot_error_trend(timestamps, error_counts):
    if not timestamps:
        print(f"{YELLOW}No error data to plot.{RESET}")
        return

    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, error_counts, marker="o", color="red", linewidth=2)
    plt.xticks(rotation=45, ha="right")
    plt.title("Error Trend Over Time")
    plt.xlabel("Timestamp")
    plt.ylabel("Error Count")
    plt.grid(True)
    plt.tight_layout()
    save_graph("error_trend.png")
    plt.show(block=True)


def plot_system_metrics(timestamps, cpu_list, ram_list, disk_list):
    plt.figure(figsize=(12, 6))

    if any(cpu_list):
        plt.plot(timestamps, cpu_list, label="CPU %", marker="o")
    if any(ram_list):
        plt.plot(timestamps, ram_list, label="RAM %", marker="o")
    if any(disk_list):
        plt.plot(timestamps, disk_list, label="Disk %", marker="o")

    plt.title("System Metrics Over Time")
    plt.xlabel("Timestamp")
    plt.ylabel("Usage (%)")
    plt.xticks(rotation=45, ha="right")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    save_graph("system_metrics.png")
    plt.show(block=True)


# ------------------------------------------------------------
# Batch Mode (N-shot)
# ------------------------------------------------------------
def process_next_n_events(n):
    if not os.path.exists(LOG_PATH):
        print(f"{RED}Log file not found at {LOG_PATH}{RESET}")
        return

    print(f"{GREEN}Processing next {n} log events...{RESET}")

    counts = {"INFO": 0, "WARNING": 0, "ERROR": 0}
    last_events = []
    event_counter = 0

    timestamps = []
    warning_counts = []
    error_counts = []
    cpu_list, ram_list, disk_list = [], [], []

    with open(LOG_PATH, "r") as f:
        for line in f:
            if event_counter >= n:
                break

            parsed = parse_log(line)
            if not parsed:
                continue

            ts, level, msg = parsed

            if level in counts:
                counts[level] += 1

            last_events.append((ts, level, msg))
            last_events = last_events[-10:]

            timestamps.append(ts)
            warning_counts.append(counts["WARNING"])
            error_counts.append(counts["ERROR"])

            cpu, ram, disk = extract_metrics(msg)
            cpu_list.append(cpu)
            ram_list.append(ram)
            disk_list.append(disk)

            event_counter += 1

    anomaly = counts["WARNING"] > 10
    render_dashboard(counts, last_events, anomaly=anomaly)

    print(f"\n{GREEN}Processed {event_counter} events. Showing graphs...{RESET}")

    plot_warning_trend(timestamps, warning_counts)
    plot_error_trend(timestamps, error_counts)
    plot_system_metrics(timestamps, cpu_list, ram_list, disk_list)


# ------------------------------------------------------------
# Last-N Mode
# ------------------------------------------------------------
def process_last_n_events(n):
    if not os.path.exists(LOG_PATH):
        print(f"{RED}Log file not found at {LOG_PATH}{RESET}")
        return

    print(f"{GREEN}Reading the last {n} log events...{RESET}")

    with open(LOG_PATH, "r") as f:
        lines = f.readlines()

    selected_lines = lines[-n:]

    counts = {"INFO": 0, "WARNING": 0, "ERROR": 0}
    last_events = []

    for line in selected_lines:
        parsed = parse_log(line)
        if not parsed:
            continue

        ts, level, msg = parsed
        if level in counts:
            counts[level] += 1

        last_events.append((ts, level, msg))

    anomaly = counts["WARNING"] > 10
    render_dashboard(counts, last_events[-10:], anomaly=anomaly)

    print(f"\n{GREEN}Displayed last {len(last_events)} events. Exiting...{RESET}")


# ------------------------------------------------------------
# Live Mode (Real-time + Live Graph)
# ------------------------------------------------------------
def run_live_mode():
    if not os.path.exists(LOG_PATH):
        print(f"{RED}Log file not found at {LOG_PATH}{RESET}")
        return

    print(f"{GREEN}Entering LIVE mode. Watching: {LOG_PATH}{RESET}")
    print(f"{YELLOW}Press CTRL + C to exit live mode.{RESET}")

    counts = {"INFO": 0, "WARNING": 0, "ERROR": 0}
    last_events = []

    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 5))
    live_x, live_y = [], []

    try:
        with open(LOG_PATH, "r") as f:
            f.seek(0, os.SEEK_END)

            while True:
                line = f.readline()

                if not line:
                    time.sleep(0.5)
                    continue

                parsed = parse_log(line)
                if not parsed:
                    continue

                ts, level, msg = parsed

                if level in counts:
                    counts[level] += 1

                last_events.append((ts, level, msg))
                last_events = last_events[-10:]

                anomaly = counts["WARNING"] > 10
                trigger_alert(level, ts, msg, counts)
                render_dashboard(counts, last_events, anomaly=anomaly)

                # Live graph update
                live_x.append(ts)
                live_y.append(counts["WARNING"])

                ax.clear()
                ax.plot(live_x, live_y, marker="o", color="orange")
                ax.set_title("Live Warning Trend")
                ax.set_xlabel("Timestamp")
                ax.set_ylabel("Warning Count")
                ax.tick_params(axis='x', rotation=45)
                plt.tight_layout()
                plt.pause(0.1)

    except KeyboardInterrupt:
        print(f"\n{GREEN}Exited live mode safely.{RESET}")
        plt.ioff()
        plt.show()


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Real-time or batch log watcher")

    parser.add_argument("--events", type=int, help="Process next N log events")
    parser.add_argument("--last", type=int, help="Process last N log events")
    parser.add_argument("--mode", choices=["live", "batch"], default="batch")

    args = parser.parse_args()

    if args.last:
        process_last_n_events(args.last)
    elif args.events:
        process_next_n_events(args.events)
    elif args.mode == "live":
        run_live_mode()
    else:
        process_next_n_events(10)


if __name__ == "__main__":
    main()