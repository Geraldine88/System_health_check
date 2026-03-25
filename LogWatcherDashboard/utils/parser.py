import logging
import re

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