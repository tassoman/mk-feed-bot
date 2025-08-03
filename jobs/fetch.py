""" Fetch Module """
import logging
import time
import sqlite3
import feedparser

def fetch_and_insert_feeds(url, db_obj):
    """ Core function """
    # Attempt to parse the feed
    data = feedparser.parse(url)

    # Check for parsing errors
    if data.bozo:
        logging.warning(data.bozo_exception)

    if data.status == 200:
        # Process the feed entries
        for entry in data.entries:
            website = data.feed.get('title', None)
            logging.debug('Website is: %s', website)

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
                c = db_obj.cursor()
                c.execute('''
                    INSERT INTO news (source, publishedAt, link, title, body)
                    VALUES (?, ?, ?, ?, ?)
                ''', (website, published_at, link, title, body))
                db_obj.commit()
            except sqlite3.IntegrityError:
                pass
            except sqlite3.OperationalError as e:
                logging.error('SQLite Operational Error: %s', e)

def add_news(db_obj):
    """ SQLite db table population """
    with open("sources.txt", encoding='utf8') as fp:
        flist = [l.strip() for l in fp if l.strip()]  # Filter out empty lines
        logging.debug('Sources count: %d', len(flist))

    # Fetch and insert feeds for each URL in "sources.txt"
    for url in flist:
        fetch_and_insert_feeds(url, db_obj=db_obj)
