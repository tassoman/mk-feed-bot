import sqlite3
import os
import time
from misskey import Misskey
from dotenv import load_dotenv

load_dotenv()

db = sqlite3.connect('OLD-feedbot.sqlite')
mk = Misskey(os.getenv('HOST'), i=os.getenv('APIKEY'))

c = db.cursor()
c.execute('SELECT noteId, title FROM news WHERE noted = 1')
q = c.fetchall()

for n in q:
    print(n)
    time.sleep(2)
    try:
        mkd = mk.notes_delete(note_id=n[0])
        print(mkd)
    except Exception as err:
        print(err)

