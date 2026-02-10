""" Fetch Module """
import logging
import os
import sqlite3
import sys
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import feedparser
import helpers

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# pylint: disable=wrong-import-position
from database import DB, init_database

helpers.debug_mode()

def install():
    """ Create SQLite DB if not exists """
    print ('DB Setup ...')
    init_database()
    logging.debug('SQLite DB was created')

def sentiment_analysis(text):
    """ Sentiment Analysis using VADER """
    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(text)
    compound_score = sentiment_score['compound']
    rounded = round(compound_score, 2)
    sample = (text[:200] + '...') if text and len(text) > 200 else text
    logging.debug('Sentiment analysis raw=%.4f rounded=%.2f sample="%s"',
                  compound_score, rounded, sample)
    return rounded

def fetch_and_insert_feeds(url):
    """ Core function """
    data = feedparser.parse(url)
    logging.debug('Fetching URL: %s', url)

    website = data.feed.get('title', None)
    logging.debug('Website is: %s', website)

    for entry in data.entries:
        # Check if 'published_parsed' exists in the entry
        if 'published_parsed' in entry:
            published_at = int(time.mktime(entry.published_parsed))
        elif 'updated_parsed' in entry:
            published_at = int(time.mktime(entry.updated_parsed))
        else:
            # Use the current time as a default value if 'published_parsed' is not present
            published_at = int(time.time())

        link = entry.link
        title = entry.title
        body = entry.summary if hasattr(entry, 'summary') else ''

        # Insert feed data into the "news" table
        try:
            with DB.get_cursor() as cursor:
                cursor.execute('''
                    INSERT INTO news (source, publishedAt, link, title, body, sentiment)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (website, published_at, link, title, body, sentiment_analysis(body)))
                logging.info('Inserted feed: %s (%s)', title, link)
        except sqlite3.IntegrityError:
            logging.debug('Duplicate entry skipped: %s', link)
        except sqlite3.OperationalError as e:
            logging.error('SQLite Operational Error: %s', e)

def add_news():
    """ SQLite db table population """
    with open("sources.txt", encoding='utf8') as fp:
        flist = [l.strip() for l in fp if l.strip()]  # Filter out empty lines
        logging.debug('Sources count: %d', len(flist))

    # Fetch and insert feeds for each URL in "sources.txt"
    for url in flist:
        fetch_and_insert_feeds(url)
