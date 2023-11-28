import sqlite3
import os
import time
from misskey import Misskey
from dotenv import load_dotenv

load_dotenv()

def purge():
    db = sqlite3.connect('feed-bot.sqlite')
    mk = Misskey(os.getenv('HOST'), i=os.getenv('APIKEY'))
    now = int(time.time())

    with db:
        c = db.cursor()
        c.execute('''
            SELECT noteId FROM news 
            WHERE notedAt < ?
            ORDER BY notedAt DESC;
        ''', (now - 60,))
        notes_to_delete = c.fetchall()

    if notes_to_delete:
        for n in notes_to_delete:
            try:
                time.sleep(2)
                denoted = mk.notes_delete(note_id=n[0])
                c.execute('DELETE FROM news WHERE noteId = ?', (n[0],))
            except Exception as err:
                print(err)
    else:
        print('No notes to delete.')

    db.close()