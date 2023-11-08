import sqlite3
import sys
import random
from .log import getlogger

logger = getlogger()


class DBManager:
    def __init__(self) -> None:
        try:
            self.conn = sqlite3.connect("user.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    email TEXT NOT NULL,
                    seed TEXT NOT NULL
                )
                """
            )
            self.conn.commit()
            db_version = self.get_db_version()
            if db_version == 0:
                self.migrate_0to1()
        except Exception as e:
            logger.error(e)
            sys.exit(1)

    def add_user(self, username, email):
        try:
            self.cursor.execute(
                """
                INSERT INTO users (username, email, seed)
                VALUES (?, ?, ?)
                """,
                (username, email, hex(random.getrandbits(64))[2:]),
            )
            self.conn.commit()
        except Exception as e:
            logger.error(e)

    def get_user_by_name(self, username):
        try:
            self.cursor.execute(
                """
                SELECT * FROM users WHERE username = ?
                """,
                (username,),
            )
            return self.cursor.fetchone()
        except Exception as e:
            logger.error(e)

    def get_user_by_email(self, email) -> str:
        try:
            self.cursor.execute(
                """
                SELECT username FROM users WHERE email = ?
                """,
                (email,),
            )
            return self.cursor.fetchone()[0]
        except Exception as e:
            logger.error(e)

    # if db version not exist, initialize and create meta table and set db_version to 0
    def get_db_version(self):
        try:
            self.cursor.execute(
                """
                SELECT db_version FROM meta
                """
            )
            return self.cursor.fetchone()[0]
        except Exception as e:
            logger.error(e)
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS meta (
                    db_version INTEGER NOT NULL
                )
                """
            )
            logger.info("meta table created")
            self.cursor.execute(
                """
                INSERT INTO meta (db_version) VALUES (0)
                """
            )
            logger.info("db_version set to 0")
            self.conn.commit()
            return 0

    def get_user_seed_by_username(self, username) -> str:
        try:
            self.cursor.execute(
                """
                SELECT seed FROM users WHERE username = ?
                """,
                (username,),
            )
            return self.cursor.fetchone()[0]
        except Exception as e:
            logger.error(e)

    def get_user_seed_by_email(self, email) -> str:
        try:
            self.cursor.execute(
                """
                SELECT seed FROM users WHERE email = ?
                """,
                (email,),
            )
            return self.cursor.fetchone()[0]
        except Exception as e:
            logger.error(e)

    def update_user_seed_by_username(self, username):
        try:
            self.cursor.execute(
                """
                UPDATE users SET seed = ? WHERE username = ?
                """,
                (hex(random.getrandbits(64))[2:], username),
            )
            self.conn.commit()
        except Exception as e:
            logger.error(e)

    def update_user_seed_by_email(self, email):
        try:
            self.cursor.execute(
                """
                UPDATE users SET seed = ? WHERE email = ?
                """,
                (hex(random.getrandbits(64))[2:], email),
            )
            self.conn.commit()
        except Exception as e:
            logger.error(e)

    # db migration from 0 to 1
    # add column seed and set random seed to existing users
    # seed: 16 hex numbers
    def migrate_0to1(self):
        try:
            self.cursor.execute(
                """
                ALTER TABLE users ADD COLUMN seed TEXT
                """
            )
            logger.info("seed column added")
            # iterate over all users and set random seed
            self.cursor.execute(
                """
                SELECT * FROM users
                """
            )
            users = self.cursor.fetchall()
            for user in users:
                self.cursor.execute(
                    """
                    UPDATE users SET seed = ? WHERE id = ?
                    """,
                    (hex(random.getrandbits(64))[2:], user[0]),
                )
            self.conn.commit()
            logger.info("seed set for all users")
            # update db_version to 1
            self.cursor.execute(
                """
                UPDATE meta SET db_version = 1
                """
            )
            self.conn.commit()
        except Exception as e:
            logger.error(e)
            sys.exit(1)
