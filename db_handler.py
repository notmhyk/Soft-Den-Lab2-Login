import sqlite3
from tkinter import messagebox
import models
import io

class DBHandler:
    def __init__(self):
        self.profile_db = 'database.db'
        self.profile_table = 'profiles'
        self.admin_table = 'admin_acc'

        self.conn = sqlite3.connect(self.profile_db)
        self.cursor = self.conn.cursor()


    def insert_account(self, profile):
        existing_email_query = f'SELECT COUNT(*) FROM {self.profile_table} WHERE email = ?'
        self.cursor.execute(existing_email_query, (profile.email,))
        existing_email_count = self.cursor.fetchone()[0]
        if existing_email_count > 0:
            messagebox.showerror('Error', "Email address already exists")
            return

        query = f'INSERT INTO {self.profile_table} (first_name, middle_name, last_name, contact_number, city, province, email, password, image) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
        values = (profile.fname, profile.mname, profile.lname, profile.contact, profile.city, profile.province, profile.email, profile.password, profile.image_data)
        self.cursor.execute(query, values)
        self.conn.commit()

    def acc_login(self, email, password):
        query = f'SELECT * FROM {self.profile_table} WHERE email =? AND password =?'
        values = (email, password)
        self.cursor.execute(query, values)
        
        result = self.cursor.fetchone()

        if result:
            return True
        else:
            return False

    def close(self):
        self.conn.close()
    