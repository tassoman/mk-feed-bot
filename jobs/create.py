from misskey import Misskey
from dotenv import load_dotenv
from datetime import datetime
import sqlite3, time, os

load_dotenv()

def publish_note():
    isLocal = os.getenv('LOCAL', 'False').lower() in ('true', '1', 't', 'on', 'ok')
    dryrun = os.getenv('DRYRUN', 'False').lower() in ('true', '1', 't', 'on', 'ok')

    db = sqlite3.connect('feed-bot.sqlite')
    c = db.cursor()
    mk = Misskey(os.getenv('HOST'), i=os.getenv('APIKEY'))

    c.execute('''
        SELECT * FROM news WHERE noted = 0 ORDER BY publishedAt DESC LIMIT 1
    ''')
    d = c.fetchone()

    if d is not None:
        text = d[1] + ": " + d[4] + "\n\n" + d[5] + "\n\n" + d[3]
        try:
            time.sleep(2)
            api = mk.notes_create(
                text=text,
                visibility=os.getenv('VISIBILITY', 'public'),
                local_only=isLocal,
            )
            
            n_id = api['createdNote']['id']
            n_at = int(datetime.strptime(
                api['createdNote']['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ'
            ).timestamp())

            c.execute('''
                UPDATE news SET noted = 1, noteId = ?, notedAt = ? WHERE id = ?
            ''', (n_id, n_at, d[0]))
            db.commit()
        except Exception as e:
            print(e)    
    db.close()
