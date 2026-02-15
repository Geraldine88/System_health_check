""""
    A Python automation tool that reads log files, extracts useful patterns, identifies
    warnings or anomalies, and generates clean, human‑readable summaries. This project
    builds on the System Health Checker by teaching me how to consume logs, not just create them.

"""
# IMPORTS
import pandas as pd
import logging
import datetime
import matplotlib.pyplot as plt
import os

# COLORS TO CODE OUTPUT USING ANSI ESCAPE CODES
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

"""

def analyze_logs(parsed_lines):
    # count INFO/WARNING/ERROR
    # detect repeated warnings
    # detect anomalies

def print_summary(results):
    # clean human-readable output

def main():
    # orchestrate everything
"""

path = '../system-health-checker/logs/sys-health-checker.log'

############### OPEN FILE #################
with open(path, 'r') as f:
    logs = f.readlines()

#print(logs)

def parse_log(line):
    """
        Parsing a single log line into timestamp, level, and message.
        Expected format:
        2026-02-13 10:00:01,123 - root - INFO - message
    """
    try:
        parts = line.split(' - ')
        time_stamp = parts[0]
        level = parts[2]
        msg = parts[3].strip()
        return time_stamp, level, msg
    except Exception as e:
        logging.error(f"Error parsing log line {line} | Error: {e}")
        return None

parse_logs = []

for line in logs:
    result = parse_log(line)
    if result:
        parse_logs.append(result)
print("Finished parsing log line")

def analyze_logs(parse_logs):
        # Count info, warning, error
        # Detect repeated warnings
        # Detect anomalies
        info_counts = 0
        warnings = 0
        errors = 0

        warning_msgs = {}
        time_stamps = []

        for log in parse_logs:
            time_stamp, level, msg = log

            if level == 'INFO':
                info_counts += 1
            elif level == 'WARNING':
                warnings += 1
                warning_msgs[msg] = warning_msgs.get(msg, 0) + 1
            elif level == 'ERROR':
                errors += 1

            # Getting timestamp to use for anomaly detection
            time_stamps.append(time_stamp)

        top_5_warnings = sorted(
            warning_msgs.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        frequent_warnings = None
        if warning_msgs:
            frequent_warnings = max(warning_msgs, key=warning_msgs.get)

        # Anomaly detection: if warnings spike above a threshold
        anomalies = warnings > 10

        return {
            'Information': info_counts,
            'Warnings': warnings,
            'Errors': errors,
            'Frequent_warnings': frequent_warnings,
            'Top_5_Warnings': top_5_warnings,
            'Anomalies': anomalies,
        }

def summary_report(results):
    print("\n===================== LOG SUMMARY ===========================")
    print(f'{GREEN}Information: {results["Information"]}{RESET}')
    print(f'{YELLOW}Warnings: {results["Warnings"]}{RESET}')
    print(f'{RED}Errors: {results["Errors"]}{RESET}')

    print('\n FREQUENT WARNINGS')
    print(results['Frequent_warnings'] if results['Frequent_warnings'] else None)

    print('\n Anomalies:')
    if results['Anomalies']:
        print(f"{RED}YES - Something strange occured{RESET}")
    else:
        print(f"{GREEN}NO - Everything looks great.{RESET}")

    print("\nTop 5 Warnings:")
    if results['Top_5_Warnings']:
        for msg, count in results['Top_5_Warnings']:
            print(f"- {msg} ({count} times)")
    else:
        print("None")
    print("===============================================================")

def bar_chart(results):
    labels = ['Information', 'Warnings', 'Errors']
    values = [
        results['Information'],
        results['Warnings'],
        results['Errors']
    ]

    plt.figure(figsize=(6,4))
    plt.bar(labels, values, color=['green', 'yellow', 'red'])
    plt.title("Log Level Summary")
    plt.xlabel("Log Level")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.grid()
    plt.show()

def export_csv(results):
    os.makedirs('exports', exist_ok=True)
    now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    filename = os.path.join('exports', f'log_sum_{now}.csv')
    df = pd.DataFrame([results])
    df.to_csv(filename, index=False)
    print(f"CSV Exported As: {filename}")

def main():
    results = analyze_logs(parse_logs)
    summary_report(results)
    export_csv(results)
    bar_chart(results)



main()
