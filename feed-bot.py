import schedule, time 
from jobs.fetch import install, add_news
from jobs.delete import purge
from jobs.create import publish_note
import os
import signal
import time

# Init
install()

### Schedules
schedule.every(5).minutes.do(add_news)
schedule.every().hour.do(purge)
schedule.every().minute.do(publish_note)

pid_file = "feed-bot.pid"

def create_pid_file():
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))

def remove_pid_file():
    if os.path.exists(pid_file):
        os.remove(pid_file)

def signal_handler(signum, frame):
    print("Exiting loop...")
    remove_pid_file()
    exit()

def main_loop():
    signal.signal(signal.SIGINT, signal_handler)

    # Check if the PID file already exists
    if os.path.exists(pid_file):
        print("Another instance is already running. Exiting.")
        exit()

    # Create PID file
    create_pid_file()

    try:
        while True:
            # Your loop logic goes here
            print("Running loop...", end='\r')
            schedule.run_pending()
            # Sleep for some time
            time.sleep(5)

    except KeyboardInterrupt:
        print(" ")
        pass
    finally:
        remove_pid_file()

if __name__ == "__main__":
    main_loop()
