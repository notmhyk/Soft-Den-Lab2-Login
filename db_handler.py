import sqlite3
import models

class DBHandler:
    def __init__(self):
        self.profile_db = 'database.db'
        self.profile_table = 'profiles'

        self.conn = sqlite3.connect(self.profile_db)
        self.cursor = self.conn.cursor()


    def insert_account(self, profile):
        query = f'INSERT INTO {self.profile_table} (first_name, middle_name, last_name, contact_number, city, province, email, password) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
        values = (profile.fname, profile.mname, profile.lname, profile.contact, profile.city, profile.province, profile.email, profile.password)
        self.cursor.execute(query, values)
        self.conn.commit()

    def close(self):
        self.conn.close()
    