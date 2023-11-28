""" feed_bot Module """
import os
import sys
import signal
import time
import schedule
from jobs.fetch import install, add_news
from jobs.delete import purge
from jobs.create import publish_note

# Init
install()

### Schedules
schedule.every(5).minutes.do(add_news)
schedule.every().hour.do(purge)
schedule.every().minute.do(publish_note)

PID_FILE = "feed-bot.pid"

def create_pid_file():
    """ Creating  pid file """
    with open(PID_FILE, 'w', encoding='utf8') as f:
        f.write(str(os.getpid()))

def remove_pid_file():
    """ Removing pid file """
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

def signal_handler():
    """ Signal handler """
    print("Exiting loop...")
    remove_pid_file()
    sys.exit()

def main_loop():
    """ Main loop """
    signal.signal(signal.SIGINT, signal_handler)

    # Check if the PID file already exists
    if os.path.exists(PID_FILE):
        print("Another instance is already running. Exiting.")
        sys.exit()

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
    finally:
        remove_pid_file()

if __name__ == "__main__":
    main_loop()
