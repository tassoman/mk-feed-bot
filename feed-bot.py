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

with open("sources.txt") as f:
    sourcelist = f.readlines()

sourcelist = [x.strip() for x in sourcelist]

load_dotenv()
db = sqlite3.connect('feedbot.sqlite')
mk = Misskey(os.getenv('MISSKEY_HOST'), i=os.getenv('MISSKEY_APIKEY'))
interval = 60 * int(os.getenv('INTERVAL', "60"))

def writeNotes():
    localOnly = os.getenv('LOCAL_ONLY', 'False').lower() in ('true', '1', 't', 'on', 'ok')
    c = db.cursor()
    c.execute("SELECT * FROM news WHERE noted = '0' ORDER BY publishedAt DESC")
    data = c.fetchall()
    db.commit()
    for row in data:
        text = row[1] + ": " + row[4] + "\n\n" + row[3]
        text = row[4] + "\n\n" + row[3]
        try: 
            note = mk.notes_create(
                text=text,
                visibility=os.getenv('VISIBILITY', 'public'),
                local_only=localOnly
                )
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
    lm = datetime.datetime.now() - datetime.timedelta(weeks=4)
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
