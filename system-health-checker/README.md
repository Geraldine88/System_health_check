# System Health Checker
A beginner‑friendly IT automation project that monitors CPU, RAM, and Disk usage, logs the results, and triggers warnings when system thresholds are exceeded. This project is part of my IT Automation → Machine Learning → Data Structures learning roadmap.

### Features
- Monitors:
- CPU usage
- RAM usage
- Disk usage
- Logs system health to a rotating log file
- Threshold‑based warnings (CPU, RAM, Disk)
- Error handling to prevent script crashes
- Daily scheduled execution
- Clean, modular, function‑based design
- Fully commented code for clarity and learning

## Project Structure
system_health_checker/
│── health_checker.py
│── logs/
│     └── sys-health-checker.log
│── README.md



### How It Works
- The script collects system metrics using psutil.
- It logs the results using Python’s logging module.
- If CPU, RAM, or Disk usage exceeds defined thresholds, a warning is written to the log.
- Logs rotate automatically to prevent large files.
- The script runs once immediately, then again daily at a scheduled time.

## Requirements
- Python 3.9+
- psutil
- schedule
Install dependencies:
pip install psutil schedule



## Running the Script
Run once immediately:
python health_checker.py


The script will then wait for the next scheduled run.

## Thresholds
Default thresholds:
CPU_THESH = 80
RAM_THESH = 80
DISK_THESH = 90




Possible Future Enhancements
- Email alerts
- Slack notifications
- CSV export of daily summaries
- GUI dashboard
- Integration with cloud monitoring tools

# Purpose of This Project
This project builds foundational automation skills:
- Logging
- Scheduling
- Error handling
- System monitoring
- Clean code structure
It is the first project in a larger roadmap that includes:
- IT automation
- Data structures
- Machine learning
- Network automation
- Real‑world engineering workflows

