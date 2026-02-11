# If any metric crosses the limit, the script writes a warning to the log.
CPU_THESH = 80
RAM_THESH = 80
DISK_THESH = 90

import psutil # a library that reads system stats
import logging # to log in data
import time
import schedule
from logging.handlers import RotatingFileHandler

print("===========================================================================")
print(" GLOBAL LOG CONFIG")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    'logs/sys-health-checker.log',
    maxBytes=1024*1024,
    backupCount=5,
)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# IMPORTANT FIX: Prevent duplicate handlers
if not logger.handlers:
    logger.addHandler(handler)

print("===============================================================================")

def sys_metrics():
    # printing out one number per cpu core
    #cpu = psutil.cpu_percent(interval=1, percpu=True)
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    return cpu, ram, disk

#creating a Log file
def log_metrics(cpu, ram, disk):
    logging.info(f"CPU Usage {cpu}%, RAM Usage {ram}%, Disk Usage {disk}%")
    # logging.basicConfig(
    #     filename='logs/sys_health.log',
    #     level=logging.INFO,
    #     format = '%(asctime)s - %(levelname)s - %(message)s',
    # )
    #
    # logging.info(f'System Health Check:\n'
    #              f'CPU: {cpu}%, \nRAM: {ram}%, \nDisk: {disk}%')

#Threshold alerts
def thresh_alerts(cpu, ram, disk):
    if cpu > CPU_THESH:
        logging.warning(f"High CPU usage detected: {cpu}%")

    if ram > RAM_THESH:
        logging.warning(f"High RAM usage detected: {ram}%")

    if disk > DISK_THESH:
        logging.warning(f"High disk usage detected: {disk}%")

# Ultimate system
def sys_main():
    try:
        cpu, ram, disk = sys_metrics()

        print(f'CPU Usage {cpu}')
        print(f'RAM Usage {ram}')
        print(f'Disk Usage {disk}')

        log_metrics(cpu, ram, disk)
        thresh_alerts(cpu, ram, disk)
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == '__main__':
    sys_main() # runs immediately
    # schedule.every(10).minutes.do(sys_main) #schedule every 10 mins
    # But I want daily checks at a particular time
    schedule.every().day.at("10:00").do(sys_main)

    while True:
        print("Waiting for next scheduled run...")
        schedule.run_pending()
        time.sleep(1)
        #sys_main()

# logging → a built‑in tool for writing logs
# subprocess → a way to run system commands
# Threshold logic → simple if‑statements

# Turn script into functions