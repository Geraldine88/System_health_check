import os

# ANSI Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

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