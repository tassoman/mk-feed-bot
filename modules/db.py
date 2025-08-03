""" SQLite3 DB Helper Module"""
import sqlite3
import logging
from modules.config import env

def open_db():
    """ Open Sqlite3 DB"""
    db = sqlite3.connect(env['db'], timeout=3, check_same_thread=True, )
    return db

def close_db(db_obj):
    """ Close DB"""
    db_obj.close()

def install_db(db_obj):
    """ Create SQLite DB if not exists """
    # Create a cursor object using the db connection
    cursor = db_obj.cursor()

    # Check if the news table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='news';")
    table_exists = cursor.fetchone()

    if not table_exists:
        # SQL command to create the news table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "news" (
                "id"    INTEGER NOT NULL UNIQUE,
                "source"        TEXT NOT NULL DEFAULT 'feed',
                "publishedAt"   INTEGER NOT NULL,
                "link"  TEXT NOT NULL UNIQUE,
                "title" TEXT NOT NULL,
                "body"  TEXT,
                "sentiment" DECIMAL(1,2),
                "noteId"        TEXT,
                "notedAt"       INTEGER,
                PRIMARY KEY("id" AUTOINCREMENT)
            );
        ''')
        db_obj.commit()
        logging.debug('DB: Created table, news')
    else:
        logging.debug('DB: Table News, already exists.')

    # Check if the feeds table already exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feeds';")
    table_exists = cursor.fetchone()

    if not table_exists:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "feeds" (
                "id"    INTEGER NOT NULL UNIQUE,
                "url"   TEXT NOT NULL UNIQUE,
                "title" TEXT,
                PRIMARY KEY("id" AUTOINCREMENT)
            );
        ''')
        logging.debug('DB: Created table, feeds')
    else:
        logging.debug('DB: Table Feeds, already exists.')
    db_obj.commit()
