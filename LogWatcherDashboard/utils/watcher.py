"""
Real-time log watcher with dashboard, alerting, and graphing.
"""

import argparse
import os
import time

from parser import parse_log, extract_metrics
from alerts import trigger_alert
from dashboard import (
    render_dashboard,
    plot_warning_trend,
    plot_error_trend,
    plot_system_metrics
)
import matplotlib.pyplot as plt


# ANSI Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

LOG_PATH = "../../system-health-checker/logs/sys-health-checker.log"

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
    render_dashboard(counts, last_events, anomaly=anomaly, log_path=LOG_PATH)

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