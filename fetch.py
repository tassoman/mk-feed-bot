#!/usr/bin/env python3
"""Feed fetching and processing module."""

import logging
import time
import sqlite3
import feedparser
from dotenv import load_dotenv
from database import DB, init_database

load_dotenv()
logger = logging.getLogger(__name__)

def install():
    """Create SQLite DB if not exists."""
    init_database()
    logger.debug('SQLite DB was created')

def fetch_and_insert_feeds(url):
    """Core function for fetching and storing feed entries.
    
    Args:
        url (str): The feed URL to process
    """
    data = feedparser.parse(url)
    logger.debug('Fetching URL: %s', url)

    website = data.feed.get('title')
    logger.debug('Website is: %s', website)

    for entry in data.entries:
        if hasattr(entry, 'published_parsed'):
            published_at = int(time.mktime(entry.published_parsed))
        elif hasattr(entry, 'updated_parsed'):
            published_at = int(time.mktime(entry.updated_parsed))
        else:
            published_at = int(time.time())

        link = entry.link
        title = entry.title
        body = entry.summary if hasattr(entry, 'summary') else ''

        try:
            with DB.get_cursor() as cursor:
                cursor.execute('''
                    INSERT INTO news (source, publishedAt, link, title, body)
                    VALUES (?, ?, ?, ?, ?)
                ''', (website, published_at, link, title, body))
        except sqlite3.IntegrityError:
            pass
        except sqlite3.OperationalError as err:
            logger.error('SQLite Operational Error: %s', err)

def add_news():
    """SQLite db table population."""
    with open("sources.txt", encoding='utf8') as feed_file:
        feed_list = [line.strip() for line in feed_file if line.strip()]
        logger.debug('Sources count: %d', len(feed_list))

    for url in feed_list:
        fetch_and_insert_feeds(url)