"""Helper functions for the feed bot"""
import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

def debug_mode():
    """ Check if debug mode is enabled """
    debug = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't', 'on', 'ok', 'v', 'vero')
    if debug:
        logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        stream=sys.stdout)
    else:
        logging.basicConfig(filename='feed_bot.log',level=logging.WARNING,
        format='%(asctime)s - %(levelname)s - %(message)s')
    return debug
