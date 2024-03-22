import sqlite3
from tkinter import messagebox
import models
import io

class DBHandler:
    def __init__(self):
        self.profile_db = 'database.db'
        self.profile_table = 'profiles'
        

        self.conn = sqlite3.connect(self.profile_db)
        self.cursor = self.conn.cursor()


    def insert_account(self, profile):
        existing_email_query = f'SELECT COUNT(*) FROM {self.profile_table} WHERE email = ?'
        self.cursor.execute(existing_email_query, (profile.email,))
        existing_email_count = self.cursor.fetchone()[0]
        if existing_email_count > 0:
            messagebox.showerror('Error', "Email address already exists")
            return

        query = f'INSERT INTO {self.profile_table} (first_name, middle_name, last_name, gender, city, province, status, email, password, image) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        values = (profile.fname, profile.mname, profile.lname, profile.gender, profile.city, profile.province, profile.status, profile.email, profile.password, profile.image_data)
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

    def email_search(self, email):
        query = f'SELECT * FROM {self.profile_table} WHERE email =?'
        values = (email,)
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()

        if result:
            return True
        else:
            return False

    def change_pass(self, email, password):
        query = f'UPDATE {self.profile_table} SET password =? WHERE email =?'
        values = (password, email)
        self.cursor.execute(query, values)
        self.conn.commit()

    def edit_info_db(self,email, fname, mname, lname, gender, city, province, status, image_data=None):
        query = f'UPDATE {self.profile_table} SET first_name = ?, middle_name = ?, last_name = ?, gender = ?, city = ?, province = ?, status = ?'
        values = (fname, mname, lname, gender, city, province, status)

        if image_data is not None:
            query += ', image = ?'
            values += (image_data,)

        query += ' WHERE email = ?'
        values += (email,)

        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            print("Profile information and image updated successfully")
        except Exception as e:
            print("Error updating profile information and image:", e)

        
    def view_account(self, key):
        if key is None:
            key = '%'
        else:
            key = '%' + key + '%'
        query = f'SELECT first_name, middle_name, last_name, gender, city, province, status, image FROM {self.profile_table} WHERE email LIKE ?'

        values = (key,)
        self.cursor.execute(query, values)

        user_info = []
        for row in self.cursor:
            user = models.Profiles()
            user.fname = row[0]
            user.mname = row[1]
            user.lname = row[2]
            user.gender = row[3]
            user.city = row[4]
            user.province = row[5]
            user.status = row[6]
            user.image_data = row[7]
            user_info.append(user)
        return user_info

    def close(self):
        self.conn.close()
    