#!/usr/bin/env python3
"""Database connection management module for mk-feed-bot."""

import sqlite3
import threading
from contextlib import contextmanager

class DatabaseConnection:
    """Thread-safe singleton database connection manager."""

    _instance = None
    _lock = threading.Lock()
    _local = threading.local()

    def __new__(cls):
        """Ensure singleton instance creation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.setup()
        return cls._instance

    def setup(self):
        """Initialize database connection settings."""
        self._lock = threading.Lock()

    @contextmanager
    def get_connection(self):
        """Get a thread-safe database connection.
        
        Yields:
            sqlite3.Connection: Database connection object
        
        Raises:
            Exception: Any database-related exception
        """
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect('feed-bot.sqlite')
            self._local.connection.row_factory = sqlite3.Row

        try:
            yield self._local.connection
        except Exception as exc:
            self._local.connection.rollback()
            raise exc
        else:
            self._local.connection.commit()

    @contextmanager
    def get_cursor(self):
        """Get a database cursor within a connection context.
        
        Yields:
            sqlite3.Cursor: Database cursor object
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
            finally:
                cursor.close()

    def close_all(self):
        """Close all database connections."""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            del self._local.connection


# Global instance
DB = DatabaseConnection()


def init_database():
    """Initialize database tables."""
    with DB.get_cursor() as cursor:
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
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "feeds" (
                "id"    INTEGER NOT NULL UNIQUE,
                "url"   TEXT NOT NULL UNIQUE,
                "title" TEXT,
                PRIMARY KEY("id" AUTOINCREMENT)
            )
        ''')