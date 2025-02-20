""" feed_bot Module """
import os
import sys
import signal
import time
import logging
import schedule
from dotenv import load_dotenv
from jobs.fetch import install, add_news
from jobs.delete import purge
from jobs.create import publish_note

load_dotenv()

debug_mode = os.getenv('DEBUG', 'False').lower() \
        in ('true', '1', 't', 'on', 'ok', 'v', 'vero')

# il debug va messo nella configurazione
if debug_mode:
    logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(filename='feed_bot.log',level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s')

# Init
install()
add_news()
publish_note()
every = os.getenv('EVERY_MINUTES', '60')

### Schedules
schedule.every(10).minutes.do(add_news)
logging.debug('Fetching Feeds every 10 minutes.')

schedule.every(int(every)).minutes.do(publish_note)
logging.debug('Posting every %s minutes.', every)

schedule.every().day.do(purge)
logging.debug('Purging posts daily')

PID_FILE = "feed-bot.pid"
logging.debug('Pid file is: %s', PID_FILE)

def create_pid_file():
    """ Creating  pid file """
    with open(PID_FILE, 'w', encoding='utf8') as f:
        f.write(str(os.getpid()))
        logging.debug('Creating pid file')

def remove_pid_file():
    """ Removing pid file """
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
        logging.debug('Removing pid file')

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
