""" feed_bot Module """
import os
import sys
import signal
import time
import logging
import schedule
from jobs.fetch import add_news
from jobs.delete import purge
from jobs.create import publish_note
from modules.config import env
from modules.db import open_db, close_db, install_db

# il debug va messo nella configurazione
if env['debug']:
    logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(filename='feed_bot.log',level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s')

db = open_db()

# Init
install_db(db)
add_news(db)
publish_note(db)

### Schedules
schedule.every(10).minutes.do(add_news, db)
logging.debug('Fetching Feeds every 10 minutes.')

schedule.every(env['frequency']).minutes.do(publish_note, db)
logging.debug('Posting every %s minutes.', env['frequency'])

schedule.every().day.do(purge, db)
logging.debug('Purging posts daily')

logging.debug('Pid file is: %s', env['pid'])

def create_pid_file():
    """ Creating  pid file """
    with open(env['pid'], 'w', encoding='utf8') as f:
        f.write(str(os.getpid()))
        logging.debug('Creating pid file')

def remove_pid_file():
    """ Removing pid file """
    if os.path.exists(env['pid']):
        os.remove(env['pid'])
        logging.debug('Removing pid file')

def signal_handler(signum, frame):
    """ Signal handler """
    logging.debug('Signal %s was recieved in frame %s.', signum, frame)
    logging.debug('Exiting Loop')
    logging.debug('Closing DB Connection')
    remove_pid_file()
    sys.exit(0)

def main_loop(db_obj):
    """ Main loop """
    signal.signal(signal.SIGINT, signal_handler)

    # Check if the PID file already exists
    if os.path.exists(env['pid']):
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
        close_db(db_obj)
        remove_pid_file()

if __name__ == "__main__":
    main_loop(db)
