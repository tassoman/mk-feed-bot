import feedparser, sqlite3, time
from dotenv import load_dotenv

load_dotenv()

def install():
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
            "noted" INTEGER NOT NULL DEFAULT 0,
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
            PRIMARY KEY("id" AUTOINCREMENT)
        );
    ''')

'''
    for url in flist:
        c = db.cursor()
        # Check if the URL already exists in the "feeds" table
        c.execute("SELECT id FROM feeds WHERE url=?", (url,))
        existing_record = c.fetchone()

        if existing_record is None:
            # If the URL doesn't exist, insert it into the "feeds" table
            c.execute("INSERT INTO feeds (url) VALUES (?)", (url,))
        else:
            print(f"URL '{url}' already exists in the 'feeds' table. Skipping.")

    # Commit changes to the database
    db.commit()
    db.close()
'''

def fetch_and_insert_feeds(url):
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

        except sqlite3.IntegrityError as e:
            pass

        db.close()

def add_news():

    with open("sources.txt") as fp:
        flist = [l.strip() for l in fp]
        fp.close()

    # Fetch and insert feeds for each URL in "sources.txt"
    for url in flist:
        fetch_and_insert_feeds(url)