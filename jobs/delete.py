""" Delete module """
import logging
import sqlite3
import time
from misskey import Misskey
from misskey.exceptions import MisskeyAPIException
from modules.config import env

def purge():
    """ Clean posts older than a month """
    db = sqlite3.connect('feed-bot.sqlite')
    mk = Misskey(env['host'], i=env['apikey'])
    now = int(time.time())

    with db:
        c = db.cursor()
        c.execute('''
            SELECT noteId FROM news
            WHERE notedAt < ?
            ORDER BY notedAt DESC;
        ''', (now - 60,))
        notes_to_delete = c.fetchall()
        logging.debug('Notes to purge: %d', len(notes_to_delete))

    if notes_to_delete:
        for n in notes_to_delete:
            time.sleep(2)
            try:
                denoted = mk.notes_delete(note_id=n[0])
                if denoted is not None:
                    c.execute('DELETE FROM news WHERE noteId = ?', (n[0],))
                    logging.debug('NoteID %s was deleted', n[0])
            except MisskeyAPIException:
                logging.warning('Misskey API Error')
    else:
        print('No notes to delete.')

    db.close()
