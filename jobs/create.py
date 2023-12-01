""" Create Module """
from datetime import datetime
import sqlite3
import time
import os
from misskey import Misskey
from dotenv import load_dotenv
from jobs.sentiment import get_sentiment

load_dotenv()

def publish_note():
    """ Takes the latest published news and posts a note """
    local_only = os.getenv('LOCAL', 'False').lower() \
        in ('true', '1', 't', 'on', 'ok')
    visibility = os.getenv('VISIBILITY', 'public').lower()
    frequency = int(os.getenv('EVERY_MINUTES', '60'))
    quantity = int(os.getenv('HOW_MANY', '1'))

    if quantity >= frequency//2:
        quantity = frequency//2-1

    db = sqlite3.connect('feed-bot.sqlite')
    c = db.cursor()
    mk = Misskey(os.getenv('HOST'), i=os.getenv('APIKEY'))

    c.execute('''
        SELECT * FROM news 
        WHERE notedAt IS NULL OR notedAt = ''
        ORDER BY publishedAt DESC LIMIT ?
    ''', str(quantity))
    data = c.fetchall()

    if data is not None:
        for d in data:
            sentiment = get_sentiment(d[4] + d[5])
            text = "\n<b>" + d[4] + "</b>\n" + d[5] + " <i>(" +d[1] + ")</i>\n\n" + d[3]
            cw = None if sentiment >= 0 else ":nsfw: News article"
            time.sleep(2)
            api = mk.notes_create(
                text=text,
                visibility=visibility,
                local_only=local_only,
                cw=cw
            )
            n_id = api['createdNote']['id']
            n_at = int(datetime.strptime(
                api['createdNote']['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ'
            ).timestamp())

            c.execute('''
                UPDATE news SET sentiment = ?, noteId = ?, notedAt = ? WHERE id = ?
            ''', (sentiment, n_id, n_at, d[0]))
            db.commit()
        db.close()
