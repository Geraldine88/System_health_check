import os
import matplotlib.pyplot as plt

# ANSI Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

# ------------------------------------------------------------
# Dashboard + Alerts
# ------------------------------------------------------------
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def render_dashboard(counts, last_events, anomaly=False, log_path=None):
    clear_screen()
    print("======  REAL-TIME LOG DASHBOARD ======")
    print(f"Watching log file:  {log_path}\n")

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