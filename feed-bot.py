import feedparser
import sqlite3
import time
import datetime
import dateutil.parser
import calendar
import json
import random
import os
from misskey import Misskey
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
pid = 'feed-bot.pid'
db = sqlite3.connect('feed-bot.sqlite')
mk = Misskey(os.getenv('HOST'), i=os.getenv('APIKEY'))
interval = int(os.getenv('MINUTES', "60"))
isLocal = os.getenv('LOCAL', 'False').lower() in ('true', '1', 't', 'on', 'ok')
dryrun = os.getenv('DRYRUN', 'False').lower() in ('true', '1','t','on','ok')

if dryrun is not True:
    interval = interval * 60

def writejob():
    c2 = db.cursor()
    q = c2.execute("SELECT * FROM news WHERE noted = 0 ORDER BY publishedAt DESC LIMIT 1")
    d = q.fetchone()
    n = {'createdNote': { 'id' : '' }}
    try:
        text = d[1] + ": " + d[4] + "\n\n" + d[5] + "\n\n" + d[3]
    except Exception as err:
        print('Non ci sono news')
        time.sleep(interval)
        return

    if dryrun is True:
        n['createdNote']['id'] = 'xxx-' + str(random.randint(111,999999))
        n['createdNote']['createdAt'] = '2022-11-25T22:04:07.069Z'
        print(text)
    else:
        try: 
            n = mk.notes_create(
                text=text,
                visibility=os.getenv('VISIBILITY', 'public'),
                local_only=isLocal
                )
        except Exception as err:
            print(err)

    try:
        c3 = db.cursor()
        createdAt = dateutil.parser.isoparse(n['createdNote']['createdAt'])
        c3.execute("UPDATE news SET noted = 1, noteid = ?,  notedAt = ? WHERE id = ? ", (n['createdNote']['id'], int(createdAt.timestamp()) , d[0]) )
        db.commit()
    except sqlite3.Error as err:
        print(err)

    time.sleep(interval)

def fetchjob():
    with open("sources.txt") as fp:
        sourcelist = fp.readlines()
        sourcelist = [x.strip() for x in sourcelist]
        for url in sourcelist:
            fetchFeed(url)

def fetchFeed(u):
    c1 = db.cursor()
    f = feedparser.parse(u)
    for i in f['entries']:
        link = i.link.split("?",1)
        updated = calendar.timegm(i.updated_parsed)
        try:
            c1.execute(
                "INSERT INTO news ( source, publishedAt, link, title, body) VALUES (?, ?, ?, ?, ?)"
                , (f.feed.title, updated , link[0], i.title, i.summary)
                )
            db.commit()
        except sqlite3.Error as err:
            continue

def purgeOld():
    lm = datetime.datetime.now() - datetime.timedelta(weeks=4)
    lastMonth = calendar.timegm(lm.timetuple())
    dbc = db.cursor()
    dbc.execute("SELECT id, noteId from news WHERE noted = 1 and publishedAt >= ?", (lastMonth,))
    data = dbc.fetchall()
    print('DATA')
    print(data)
    for row in data:
        if dryrun is not True:
            try:
                api = mk.notes_delete(note_id=row[1])
                if (api is True):
                    db.execute("DELETE from news WHERE id = ?", (row[0],))
            except Exception as err:
                print(err)
            finally:
                time.sleep(2)
        else:
            print(row)
            try:
                db.execute("DELETE from news WHERE id = ?", (row[0],))
                time.sleep(1)
            except Exception as err:
                print(err)

    time.sleep(1)
    db.commit()

# MAIN LOOP

Path(pid).touch()
while (os.path.exists(pid)):
    fetchjob()
    writejob()
#    purgeOld()

db.close()
print('Exit')