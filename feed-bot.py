import feedparser
import sqlite3
import time
import datetime
import calendar
import json
import os
from misskey import Misskey
from pathlib import Path
from dotenv import load_dotenv

sourcelist = [
    'http://rss.slashdot.org/Slashdot/slashdotMain?format=xml',
    'https://techcrunch.com/feed/',
    'http://www.theverge.com/rss/frontpage',''
    'https://mashable.com/feeds/rss/all',
    'https://www.wired.com/feed/rss',
    'https://gizmodo.com/rss',
    'https://www.cnet.com/rss/news/',
    'https://www.engadget.com/rss.xml',
    'https://www.zdnet.com/news/rss.xml',
    'http://rss.nytimes.com/services/xml/rss/nyt/Technology.xml',
    'http://feeds.bbci.co.uk/news/technology/rss.xml',
    'http://feeds.howtogeek.com/HowToGeek',
    'http://feeds.arstechnica.com/arstechnica/technology-lab',
]

load_dotenv()
db = sqlite3.connect('feedbot.sqlite')
mk = Misskey('misskey.social', i=os.getenv('MISSKEY_APIKEY'))
interval = 60*5

def writeNotes():
    c = db.cursor()
    c.execute("SELECT * FROM news WHERE noted = '0' ORDER BY publishedAt DESC")
    data = c.fetchall()
    db.commit()
    for row in data:
#        text = row[1] + ": " + row[4] + "\n\n" + row[3]
        text = row[4] + "\n\n" + row[3]
        try: 
            note = mk.notes_create(text=text)
            cc = db.cursor()
            try:
                cc.execute("UPDATE news SET noted = 1, noteid = ? WHERE id = ? ", (note['createdNote']['id'], row[0]) )
                db.commit()
            except sqlite3.Error as err:
                print(err)
        except Exception as err:
            print(err)
        
        time.sleep(interval)

def fetchRSS(feed):
    c = db.cursor()
    feed = feedparser.parse(feed)
    for item in feed['entries']:
        link = item.link.split("?",1)
        updated = calendar.timegm(item.updated_parsed)
        try:
            c.execute(
                "INSERT INTO news ( source, publishedAt, link, title ) VALUES (?, ?, ?, ?)"
                , (feed.feed.title, updated , link[0], item.title))
            db.commit()
        except sqlite3.Error as err:
            print(err)

def deleteOldNotes():
    lm = datetime.datetime.now() - datetime.timedelta(minutes=4)
    lastMonth = calendar.timegm(lm.timetuple())
    dbc = db.cursor()
    dbc.execute("SELECT id, noteId from news WHERE noted = 1 and publishedAt <= ?", (lastMonth,))
    data = dbc.fetchall()
    for row in data:
        try:
            api = mk.notes_delete(note_id=row[1])
            if (api is True):
                db.execute("DELETE from news WHERE id = ?", (row[0],))
        except Exception as err:
            print(err)
        finally:
            time.sleep(2)

    db.commit()
                


Path('feedbot.pid').touch()
while (os.path.exists('feedbot.pid')):
    for url in sourcelist:
        fetchRSS(url)
    
    writeNotes()
    deleteOldNotes()
    time.sleep(interval)
else:
    print("uscita!")
    db.close()
