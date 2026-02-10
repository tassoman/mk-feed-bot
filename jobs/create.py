""" Create Module """
from datetime import datetime
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

## Questo va spostato nella configurazione
env = {
    'local_only': os.getenv('LOCAL', 'False').lower() \
        in ('true', '1', 't', 'on', 'ok', 'v', 'vero'),
    'visibility': os.getenv('VISIBILITY', 'public').lower(),
    'frequency': int(os.getenv('EVERY_MINUTES', '60')),
    'quantity': int(os.getenv('HOW_MANY', '1')),
    'sentiment': float(os.getenv('SENTIMENT', '0.05'))
}
logging.debug('Configuration loaded: %s', env)

def publish_note():
    """ Takes the latest published news and posts a note """
    if env['frequency'] == 2:
        env['quantity'] = 1
    elif env['frequency'] == 1:
        env['quantity'] = 1
    else:
        if env['quantity'] >= env['frequency']//2:
            env['quantity'] = env['frequency']//2-1
    logging.debug('Amount chosen: %d', env['quantity'])

    mk = Misskey(os.getenv('HOST'), i=os.getenv('APIKEY'))

    with DB.get_cursor() as cursor:
        cursor.execute('''
            SELECT * FROM news
            WHERE notedAt IS NULL OR notedAt = ''
            ORDER BY publishedAt DESC LIMIT ?
        ''', str(env['quantity']))
        data = cursor.fetchall()
    logging.debug('Posting %d notes', len(data))

    if data is not None:
        for d in data:
            raw_sentiment = d[6]
            try:
                if raw_sentiment is not None and raw_sentiment != '':
                    sentiment_val = float(raw_sentiment)
                else:
                    sentiment_val = 0.0

            except (TypeError, ValueError):
                sentiment_val = 0.0

            note_params = {
                'sentiment': sentiment_val,
                'text': "\n<b>" + d[4] + "</b>\n" + d[5] + " <i>(" + d[1] + ")</i>\n\n" + d[3],
                'cw': None
            }

            logging.debug('Preparing note for id=%s sentiment=%s', d[0], note_params['sentiment'])

            if note_params['sentiment'] < env['sentiment']:
                note_params['cw'] = ":nsfw: News article flagged CW"
                logging.warning('Article id=%s flagged CW (sentiment=%.2f < %s)',
                                d[0],
                                note_params['sentiment'],
                                env['sentiment']
                )
            else:
                logging.debug('Article id=%s passed sentiment threshold (%.2f >= %s)',
                              d[0],
                              note_params['sentiment'],
                              env['sentiment']
                )
            time.sleep(2)
            try:
                logging.info('Posting note for news id=%s', d[0])
                api = mk.notes_create(
                    text=note_params['text'],
                    visibility=env['visibility'],
                    local_only=env['local_only'],
                    cw=note_params['cw']
                )
                n_id = api['createdNote']['id']
                n_at = int(datetime.strptime(
                    api['createdNote']['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ'
                ).timestamp())
                logging.debug('Created Note: %s', api)

                with DB.get_cursor() as cursor:
                    cursor.execute('''
                        UPDATE news SET sentiment = ?, noteId = ?, notedAt = ? WHERE id = ?
                    ''', (note_params['sentiment'], n_id, n_at, d[0]))
                    logging.info('Updated DB for news id=%s with noteId=%s', d[0], n_id)
            except MisskeyAPIException as e:
                print(f"MK API error: {e}")
                logging.error('Misskey API Error: %s', e)
