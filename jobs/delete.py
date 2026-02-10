""" Delete module """
import logging
import os
import sys
import time

from misskey import Misskey
from misskey.exceptions import MisskeyAPIException
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# pylint: disable=wrong-import-position
from database import DB

load_dotenv()

def purge():
    """ Clean posts older than a month """
    mk = Misskey(os.getenv('HOST'), i=os.getenv('APIKEY'))
    now = int(time.time())

    with DB.get_cursor() as cursor:
        cursor.execute('''
            SELECT noteId FROM news
            WHERE notedAt < ?
            ORDER BY notedAt DESC;
        ''', (now - 60,))
        notes_to_delete = cursor.fetchall()
    logging.debug('Notes to purge: %d', len(notes_to_delete))

    if notes_to_delete:
        for n in notes_to_delete:
            time.sleep(2)
            try:
                denoted = mk.notes_delete(note_id=n[0])
                if denoted is not None:
                    with DB.get_cursor() as cursor:
                        cursor.execute('DELETE FROM news WHERE noteId = ?', (n[0],))
                    logging.debug('NoteID %s was deleted', n[0])
            except MisskeyAPIException:
                logging.warning('Misskey API Error')
    else:
        print('No notes to delete.')
