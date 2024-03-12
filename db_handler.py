import sqlite3
import models

class DBHandler:
    def __init__(self):
        self.profile_db = 'database.db'
        self.profile_table = 'profiles'

        self.conn = sqlite3.connect(self.profile_db)
        self.cursor = self.conn.cursor()
    