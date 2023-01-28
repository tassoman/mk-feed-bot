import feedparser
import sqlite3
import time
import datetime
import dateutil.parser
import calendar
import json
import random
import os
import shutil
from misskey import Misskey
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

pid = 'feed-bot.pid'
db = sqlite3.connect('feed-bot.sqlite')
mk = Misskey(os.getenv('HOST'), i=os.getenv('APIKEY'))
interval = int(os.getenv('MINUTES', "60"))
isLocal = os.getenv('LOCAL', 'False').lower() in ('true', '1', 't', 'on', 'ok')
dryrun = os.getenv('DRYRUN', 'False').lower() in ('true', '1', 't', 'on', 'ok')

if dryrun is True:
    try:
        shutil.copyfile('feed-bot.sqlite_EXAMPLE', 'feed-bot.sqlite')
    except:
        pass
else:
    interval = interval * 60

with open("sources.txt") as fp:
    sourcelist = fp.readlines()
    sourcelist = [x.strip() for x in sourcelist]

for u in sourcelist:
    if dryrun is True:
        print('SOURCE: ' + u)
    cu = db.cursor()
    cu.execute("INSERT INTO feeds (url) VALUES (?)", (u,))
    db.commit()


def writejob():
    cn = db.cursor()
    q = cn.execute(
        "SELECT * FROM news WHERE noted = 0 ORDER BY publishedAt DESC LIMIT 1")
    d = q.fetchone()
    n = {'createdNote': {'id': ''}}
    try:
        text = d[1] + ": " + d[4] + "\n\n" + d[5] + "\n\n" + d[3]
    except Exception as err:
        print('Non ci sono news')
        time.sleep(interval)
        return

    if dryrun is True:
        n['createdNote']['id'] = 'xxx-' + str(random.randint(111, 999999))
        n['createdNote']['createdAt'] = '2022-11-25T22:04:07.069Z'
        print(datetime.datetime.utcfromtimestamp(
            d[2]).strftime('%Y-%m-%d %H:%M:%S'))
        print(text)
        print('. - = - = - = - = - = ^ = - = - = - = - = - = - .')
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
        cu = db.cursor()
        createdAt = dateutil.parser.isoparse(n['createdNote']['createdAt'])
        cu.execute("UPDATE news SET noted = 1, noteid = ?,  notedAt = ? WHERE id = ? ",
                   (n['createdNote']['id'], int(createdAt.timestamp()), d[0]))
        db.commit()
    except sqlite3.Error as err:
        print(err)

    time.sleep(interval)


def fetchAllJobs():
    cff = db.cursor()
    q = cff.execute('SELECT * FROM feeds')
    ff = q.fetchall()

    for f in ff:
        fetchFeed(f[0], f[2])


def fetchFeed(url: str, modified):
    if dryrun is True:
        print('Fetch Feed:' + url)
    ci = db.cursor()
    f = feedparser.parse(url, modified=modified)
    for i in f['entries']:
        link = i.link.split("?", 1)
        updated = calendar.timegm(i.updated_parsed)
        try:
            ci.execute(
                "INSERT INTO news ( source, publishedAt, link, title, body) VALUES (?, ?, ?, ?, ?)", (
                    f.feed.title, updated, link[0], i.title, i.summary)
            )
            db.commit()

            if hasattr(f, 'etag'):
                ce = db.cursor()
                ce.execute(
                    'UPDATE feeds SET etag = ? WHERE url = ?', (f.etag, url,))
                db.commit()

            if hasattr(f, 'modified'):
                cm = db.cursor()
                cm.execute('UPDATE feeds SET modified = ? WHERE url = ?',
                           (f.modified, url,))
                db.commit()
        except sqlite3.Error as err:
            continue


def purgeOld():
    lm = datetime.datetime.now() - datetime.timedelta(weeks=4)
    lastMonth = calendar.timegm(lm.timetuple())
    cp = db.cursor()
    cp.execute(
        "SELECT id, noteId from news WHERE noted = 1 and publishedAt >= ?", (lastMonth,))
    data = cp.fetchall()
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
            print('Purge Row:')
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
    if dryrun is True:
        print('While Loop:')

    cl = db.cursor()
    q = cl.execute("SELECT COUNT(*) FROM news WHERE noted = 0")
    towrite = q.fetchone()
    if dryrun is True:
        print('Quante: ' + '{:d}'.format(towrite[0]))

    if (towrite[0] > 0):
        if dryrun is True:
            print('TO WRITE')

        writejob()

    else:
        if dryrun is True:
            print('TO PURGE')
            print('TO FETCH')

        # purgeOld()
        fetchAllJobs()

    time.sleep(1)

db.close()
print('Exit')
