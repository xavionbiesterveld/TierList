import sqlite3
from logger import get_logger

class db():
    def __init__(self, db_name='app.db'):
        self.db_name = db_name
        self.logger = get_logger(__name__)

        self.logger.info(f"Initializing database: {self.db_name}")

        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

        try:
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tier_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_title TEXT UNIQUE,
            show_title TEXT,
            a_id INTEGER,
            mal_score REAL,
            rank INTEGER,
            popularity INTEGER,
            genres TEXT,
            start_season TEXT,
            tier TEXT,
            score_v INTEGER,
            score_mus INTEGER,
            score_n INTEGER,
            score_mem INTEGER)
            ''')

            self.logger.info(f"Database initialized successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Error creating table: {e}")
        finally:
            self.cursor.close()
            self.conn.close()

    def refresh_db(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

        try:
            self.cursor.execute('''
                DROP TABLE tier_list
            ''')

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS tier_list
                (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     song_title TEXT UNIQUE,
                     show_title TEXT,
                     a_id INTEGER,
                     mal_score REAL,
                     rank INTEGER,
                     popularity INTEGER,
                     genres TEXT,
                     start_season TEXT,
                     tier TEXT,
                     score_v INTEGER,
                     score_mus INTEGER,
                     score_n INTEGER,
                     score_mem INTEGER
                )''')
            self.logger.info(f"Database Refreshed successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Error refreshing table: {e}")
        finally:
            self.cursor.close()
            self.conn.close()

    def insert_data(self, name, info, scores):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.logger.info(f"Inserting data for opening {name['text']} into database: {self.db_name}")

        genres = []
        for genre in info['genres']:
            genres.append(genre['name'])

        final_score = 0
        for score in scores:
            final_score += score

        if final_score >= 36:
            tier = "S"
        elif final_score >= 30:
            tier = "A"
        elif final_score >= 24:
            tier = "B"
        else:
            tier = "C"

        season = str(info['start_season']['season']) + ", " + str(info['start_season']['year'])

        try:
            self.cursor.execute('''
            INSERT INTO tier_list (song_title, show_title, a_id, mal_score, rank, popularity, genres, start_season, tier, score_v, score_mus, score_n, score_mem)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name['text'], info['title'], info['id'], info['mean'], info['rank'], info['popularity'], str(genres), season, tier, scores[0], scores[1], scores[2], scores[3] ))

            self.conn.commit()

            self.logger.info(f"Data inserted successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting data: {e}")
        finally:
            self.cursor.close()
            self.conn.close()

    def find_if_exists(self,name):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.logger.debug(f"Checking if {name} exists in database: {self.db_name}")

if __name__ == '__main__':
    db = db()
    db.refresh_db()
