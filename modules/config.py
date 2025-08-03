""" Configuration module"""
import os
from dotenv import load_dotenv

load_dotenv()

env = {
    'debug': os.getenv('DEBUG', 'False').lower() \
        in ('true', '1', 't', 'on', 'ok', 'v', 'vero', 'yes'),
    'local_only': os.getenv('LOCAL', 'False').lower() \
        in ('true', '1', 't', 'on', 'ok', 'v', 'vero', 'yes'),
    'visibility': os.getenv('VISIBILITY', 'public').lower(),
    'frequency': int(os.getenv('EVERY_MINUTES', '60')),
    'quantity': int(os.getenv('HOW_MANY', '1')),
    'host': os.getenv('HOST', 'localhost'),
    'apikey': os.getenv('APIKEY', 'abc123'),
    'pid': 'feed-bot.pid',
    'db' : 'feed-bot.sqlite'
}
