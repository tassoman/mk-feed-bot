""" Fetch Module """
import time
import sqlite3
import feedparser
from dotenv import load_dotenv

load_dotenv()

def install():
    """ Create SQLite DB if not exists """
    print ('DB Setup ...')
    db = sqlite3.connect('feed-bot.sqlite')
    c = db.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS "news" (
            "id"    INTEGER NOT NULL UNIQUE,
            "source"        TEXT NOT NULL DEFAULT 'feed',
            "publishedAt"   INTEGER NOT NULL,
            "link"  TEXT NOT NULL UNIQUE,
            "title" TEXT NOT NULL,
            "body"  TEXT,
            "sentiment" DECIMAL(1,2),
            "noteId"        TEXT,
            "notedAt"       INTEGER,
            PRIMARY KEY("id" AUTOINCREMENT)
        );
    ''')
    db.commit()

    c.execute('''
        CREATE TABLE IF NOT EXISTS "feeds" (
            "id"    INTEGER NOT NULL UNIQUE,
            "url"   TEXT NOT NULL UNIQUE,
            "title" TEXT,
            PRIMARY KEY("id" AUTOINCREMENT)
        );
    ''')

def fetch_and_insert_feeds(url):
    """ Core function """
    feed = feedparser.parse(url)
    website = feed.feed.title

    for entry in feed.entries:
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
        db = sqlite3.connect('feed-bot.sqlite')
        c = db.cursor()

        try:
            c.execute('''
                INSERT INTO news (source, publishedAt, link, title, body)
                VALUES (?, ?, ?, ?, ?)
            ''', (website, published_at, link, title, body))
            db.commit()

        except sqlite3.IntegrityError:
            pass

        db.close()

def add_news():
    """ SQLite db table population """
    with open("sources.txt", encoding='utf8') as fp:
        flist = [l.strip() for l in fp]
        fp.close()

    # Fetch and insert feeds for each URL in "sources.txt"
    for url in flist:
        fetch_and_insert_feeds(url)
