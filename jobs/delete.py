""" Delete module """
import sqlite3
import os
import time
from misskey import Misskey
from dotenv import load_dotenv

load_dotenv()

def purge():
    """ Clean posts older than a month """
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
            time.sleep(2)
            try:
                denoted = mk.notes_delete(note_id=n[0])
            except Misskey.exceptions.MisskeyAPIException:
                pass
            if denoted is not None:
                c.execute('DELETE FROM news WHERE noteId = ?', (n[0],))
    else:
        print('No notes to delete.')

    db.close()
