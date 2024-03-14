import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import filedialog, simpledialog
from PIL import Image, ImageTk
from tkinter import messagebox
import sqlite3
import db_handler
import models
import re
import io

class FadingLabel(tk.Label):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.default_color = self['background']
        self.hover_color = "#00FF00"
        self.fade_out_color = "#121212" 
        self.fade_steps = 10 
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.config(highlightbackground='#121212', highlightthickness=2)
    
    def on_enter(self, event):
        self.config(background=self.fade_out_color, highlightbackground=self.hover_color)

    def on_leave(self, event):
        self.fade_to_black()

    def fade_to_black(self):
        self.fade_step = 0
        self.fade_out_recursive()

    def fade_out_recursive(self):
        if self.fade_step <= self.fade_steps:
            fade_factor = self.fade_step / self.fade_steps
            r = int((1 - fade_factor) * int(self.hover_color[1:3], 16) + fade_factor * int(self.fade_out_color[1:3], 16))
            g = int((1 - fade_factor) * int(self.hover_color[3:5], 16) + fade_factor * int(self.fade_out_color[3:5], 16))
            b = int((1 - fade_factor) * int(self.hover_color[5:], 16) + fade_factor * int(self.fade_out_color[5:], 16))
            new_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
            self.config(highlightbackground=new_color)
            self.fade_step += 1
            self.after(100, self.fade_out_recursive)
        else:
            self.config(highlightbackground=self.fade_out_color)

class LoginPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.parent = master
        self.config(background='black')

        self.create_labels()
        self.show_canvas()

    def create_labels(self):
        labels = []
        for i in range(10):
            for j in range(20):
                label = FadingLabel(self, text="", width=10, height=4, background="#121212")
                label.grid(row=i, column=j, padx=2, pady=2, ipadx=1, ipady=1)
                labels.append(label)

    def show_canvas(self):
        self.canvas_width = 600
        self.canvas_height = 500
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg='#0c0c0c', 
                                highlightbackground='#00FF00', highlightthickness=2)
        self.canvas.grid(row=1, column=4, rowspan=7, columnspan=8, sticky='nsew')
        self.show_object()

    def show_object(self):
        
        self.sign_in_lb = tk.Label(self, text="SIGN IN", font=("Montserrat", 30, "bold"),
                                     fg='#00FF00', bg='#0c0c0c')
        self.canvas.create_window(self.canvas_width // 1.75 , self.canvas_height // 6, window=self.sign_in_lb)

        self.entry_email = tk.Entry(self, font=('Monospac821 BT', 17), width=30, justify='center', fg='white', bg='#323232')
        self.canvas.create_window(self.canvas_width // 1.75 , self.canvas_height // 3, window=self.entry_email)

        self.entry_email.insert(0, 'Email')
        

        self.entry_pass = tk.Entry(self, font=('Monospac821 BT', 17), width=30, justify='center', fg='white', bg='#323232')
        self.canvas.create_window(self.canvas_width // 1.75 , self.canvas_height // 2, window=self.entry_pass)

        self.entry_pass.insert(0, 'Password')

        self.login_btn = tk.Button(self, text='LOGIN', font=('Montserrat', 17, 'bold'), 
                                   fg='#00FF00', bg='#0c0c0c', width=25, cursor='hand2', command=self.onclick_login)
        self.canvas.create_window(self.canvas_width // 1.75 , self.canvas_height // 1.3, window=self.login_btn)

        self.forgot_pass_label = tk.Label(self, text='Forgot Password', font=('Monospac821 BT', 11, 'underline'), 
                                          bg='#0c0c0c', fg='white', cursor='hand2')
        self.canvas.create_window(self.canvas_width // 3.4 , self.canvas_height // 1.6, window=self.forgot_pass_label)

        self.signup_label = tk.Label(self, text='SIGN-UP', font=('Monospac821 BT', 11), bg='#0c0c0c', fg='#00FF00', cursor='hand2')
        self.canvas.create_window(self.canvas_width // 1.11 , self.canvas_height // 1.6, window=self.signup_label)

        self.bind()

    def onclick_login(self):
        email = self.entry_email.get()
        password = self.entry_pass.get()
        
        if email == '':
            messagebox.showerror('Error', 'Email cannot be empty')
            return
        elif password == '':
            messagebox.showerror('Error', 'Password cannot be empty')
            return
        
        if self.parent.db_handler.acc_login(email, password):
            self.parent.change_frame('LandingPage')
        elif self.parent.db_handler.admin_login(email, password):
            self.parent.change_frame('AdminPage')
        else:
            messagebox.showerror("Invalid Login", "Invalid username or password")
        

    def bind(self):
        self.entry_pass.bind('<FocusIn>', self.entry_pass_enter)
        self.entry_pass.bind('<FocusOut>', self.entry_pass_leave)
        self.signup_label.bind('<Button-1>', self.on_click_sign_up)
        self.entry_email.bind('<FocusIn>', self.entry_user_enter)
        self.entry_email.bind('<FocusOut>', self.entry_user_leave)
        self.canvas.bind('<Button-1>', self.canvas_clicked)

    def on_click_sign_up(self, event):
        self.parent.change_frame('SignUpPage')

    def entry_user_enter(self, event):
        if self.entry_email.get() == 'Email':
            self.entry_email.delete(0, tk.END)
            self.entry_email.insert(0, '')

    def entry_user_leave(self, event):
        if self.entry_email.get() == '':
            self.entry_email.delete(0, tk.END)
            self.entry_email.insert(0, 'Email')
        
    def entry_pass_enter(self, event):
        if self.entry_pass.get() == 'Password':
            self.entry_pass.delete(0, tk.END)
            self.entry_pass.insert(0, '')
            self.entry_pass.config(show='*')
    
    def entry_pass_leave(self, event):
        if self.entry_pass.get() == '':
            self.entry_pass.delete(0, tk.END)
            self.entry_pass.insert(0, 'Password')
            self.entry_pass.config(show='')

    def canvas_clicked(self, event):
        if not self.entry_pass.get() or not self.entry_email.get():
            self.focus_set()
        else:
            self.focus_set()
        

class SignUpPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.parent = master
        
        self.config(background='black')
        self.create_labels()
        self.show_canvas()
        
    def create_labels(self):
        labels = []
        for i in range(10):
            for j in range(20):
                label = FadingLabel(self, text="", width=10, height=4, background="#121212")
                label.grid(row=i, column=j, padx=2, pady=2, ipadx=1, ipady=1)
                labels.append(label)

    def show_canvas(self):
        self.canvas_width = 600
        self.canvas_height = 500
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg='#0c0c0c', highlightbackground='#00FF00', highlightthickness=2)
        self.canvas.grid(row=1, column=2, rowspan=7, columnspan=12, sticky='nsew')
        self.show_object()
        
    def show_object(self):
        self.chk_box_var = tk.BooleanVar()
        self.image_path = 'border.png'
        
        self.image_pil = Image.open(self.image_path)
        self.resize_image = self.image_pil.resize((330,220))
        self.image = ImageTk.PhotoImage(self.resize_image)
        self.canvas.create_image(self.canvas_width // 3, self.canvas_height // 2.6, image=self.image)
        
        self.label = tk.Label(self, text='Create Account', font=('Montserrat', 25, 'bold'), fg='#00FF00', bg='#0c0c0c')
        self.canvas.create_window(self.canvas_width // 1.4, self.canvas_height // 15, window=self.label)

        self.personal_label = tk.Label(self, text='Personal Info', font=('Monospac821 BT', 11), fg='#00FF00', bg='#0c0c0c')
        self.canvas.create_window(self.canvas_width // 7, self.canvas_height // 6, window=self.personal_label)

        self.fname_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=20, justify='center', fg='white', bg='#323232')
        self.canvas.create_window(self.canvas_width // 3, self.canvas_height // 3.7, window=self.fname_entry)

        self.mname_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=20, justify='center', fg='white', bg='#323232')
        self.canvas.create_window(self.canvas_width // 3, self.canvas_height // 2.6, window=self.mname_entry)

        self.lname_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=20, justify='center', fg='white', bg='#323232')
        self.canvas.create_window(self.canvas_width // 3, self.canvas_height // 2, window=self.lname_entry)
        

        self.image_pil2 = Image.open(self.image_path)
        self.resize_image2 = self.image_pil2.resize((330,210))
        self.image2 = ImageTk.PhotoImage(self.resize_image2)
        self.canvas.create_image(self.canvas_width // 3, self.canvas_height // 1.2, image=self.image2)

        self.other_label = tk.Label(self, text='Other Info', font=('Monospac821 BT', 11), fg='#00FF00', bg='#0c0c0c')
        self.canvas.create_window(self.canvas_width // 7, self.canvas_height // 1.6, window=self.other_label)

        self.contact_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=20, justify='center', fg='white', bg='#323232')
        self.canvas.create_window(self.canvas_width // 3, self.canvas_height // 1.4, window=self.contact_entry)

        self.city_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=20, justify='center', fg='white', bg='#323232')
        self.canvas.create_window(self.canvas_width // 3, self.canvas_height // 1.2, window=self.city_entry)

        self.province_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=20, justify='center', fg='white', bg='#323232')
        self.canvas.create_window(self.canvas_width // 3, self.canvas_height // 1.05, window=self.province_entry)

        self.account_label = tk.Label(self, text='Account Info', font=('Monospac821 BT', 11), fg='#00FF00', bg='#0c0c0c')
        self.canvas.create_window(self.canvas_width // 1.5, self.canvas_height // 6, window=self.account_label)

        self.email_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=30, justify='center', fg='white', bg='#323232')
        self.canvas.create_window(self.canvas_width // 1.1, self.canvas_height // 3.7, window=self.email_entry)

        self.pass_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=30, justify='center', fg='white', bg='#323232')
        self.canvas.create_window(self.canvas_width // 1.1, self.canvas_height // 2.7, window=self.pass_entry)

        self.confirm_pass_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=30, justify='center', fg='white', bg='#323232')
        self.canvas.create_window(self.canvas_width // 1.1, self.canvas_height // 2.2, window=self.confirm_pass_entry)

        self.terms_condition_lb = tk.Label(self, text='Terms & Conditions', font=('Monospac821 BT', 11), fg='#00FF00', bg='#0c0c0c')
        self.canvas.create_window(self.canvas_width // 1.3, self.canvas_height // 1.95, window=self.terms_condition_lb)
        terms_condition_txt = """
Terms and Conditions: Login, Security, and User Compliance

1. Login Credentials: Users are required to create and maintain login credentials (username and password) that are unique and confidential. Sharing of login information is strictly prohibited.

2. Security Measures: The platform employs industry-standard security measures to protect user information and identity. Users are responsible for maintaining the security of their accounts and promptly reporting any unauthorized access or suspicious activity.

3. Protection of Information: All user data, including personal and sensitive information, is handled in accordance with our privacy policy. We are committed to safeguarding user privacy and will not disclose or sell user information to third parties without consent, except as required by law.

4. Identity Verification: Users must provide accurate and truthful information during registration and identity verification processes. Falsifying identity or providing misleading information is grounds for account suspension or termination.

5. Compliance with Rules: By accessing the platform, users agree to abide by all applicable laws, regulations, and the terms outlined in this agreement. Any violation of these terms may result in disciplinary action, including account suspension or legal consequences.

6. Responsibility for Actions: Users are solely responsible for their actions while using the platform. This includes adherence to community guidelines, respect for intellectual property rights, and refraining from engaging in illegal or harmful activities.

7. Updates and Modifications: These terms and conditions may be updated or modified periodically to reflect changes in regulations or improvements to the platform. Users will be notified of any significant changes, and continued use of the platform constitutes acceptance of the updated terms.

8. Termination of Access: We reserve the right to terminate or suspend user access to the platform at any time, without prior notice, for violations of these terms or any other reason deemed necessary to protect the integrity of the platform.

By logging into the platform, users acknowledge that they have read, understood, and agreed to abide by these terms and conditions regarding login, security, and user compliance.
"""

        self.text_box_terms_conditions = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=35, height=6)
        self.text_box_terms_conditions.insert(tk.END, terms_condition_txt)
        self.text_box_terms_conditions.tag_configure("color", foreground="#00FF00", background='#0c0c0c') 
        self.text_box_terms_conditions.tag_add("color", "2.0", "end")
        self.canvas.create_window(self.canvas_width // 1.1, self.canvas_height // 1.58, window=self.text_box_terms_conditions)

        self.chk_btn = tk.Checkbutton(self, text='Agree to terms', variable=self.chk_box_var, fg='#00FF00', bg='#0c0c0c', font=('Monospac821 BT', 11))
        self.canvas.create_window(self.canvas_width // 1.1, self.canvas_height // 1.28, window=self.chk_btn)

        self.image_pil3 = Image.open(self.image_path)
        self.resize_image3 = self.image_pil3.resize((420,380))
        self.image3 = ImageTk.PhotoImage(self.resize_image3)
        self.canvas.create_image(self.canvas_width // 1.1, self.canvas_height // 1.94, image=self.image3)

        self.create_btn = tk.Button(self, text='Create Account', font=('Montserrat', 14, 'bold'), 
                                   fg='#00FF00', bg='#0c0c0c', width=15, cursor='hand2', command=self.onclick_create)
        self.canvas.create_window(self.canvas_width // 1.1 , self.canvas_height // 1.06, window=self.create_btn)

        self.back_image_path = 'back.png'
        self.pil_image_back_image = Image.open(self.back_image_path)
        self.resize_back_image = self.pil_image_back_image.resize((30,30))
        self.image_back_image = ImageTk.PhotoImage(self.resize_back_image)
        self.back_button = tk.Label(self, image=self.image_back_image, bg='#0c0c0c', cursor='hand2')
        self.canvas.create_window(self.canvas_width // 0.62, self.canvas_height // 10, window=self.back_button)

        self.image_label = tk.Label(self, text='No Image Uploaded', font=('Monospac821 BT', 12), fg='#00FF00', bg='#0c0c0c')
        self.canvas.create_window(self.canvas_width // 0.69, self.canvas_height // 2.4, window=self.image_label)

        self.crop_btn = tk.Button(self, text='Crop', font=('Montserrat', 14, 'bold'), 
                                   fg='#00FF00', bg='#0c0c0c', width=15, cursor='hand2', command=self.start_crop)
        self.canvas.create_window(self.canvas_width // 0.69 , self.canvas_height // 1.4, window=self.crop_btn)

        self.upload_btn = tk.Button(self, text='Upload Image', font=('Montserrat', 14, 'bold'), 
                                   fg='#00FF00', bg='#0c0c0c', width=15, cursor='hand2', command=self.upload_image)
        self.canvas.create_window(self.canvas_width // 0.69 , self.canvas_height // 1.2, window=self.upload_btn)
        
        self.retrieve_image = tk.Button(self, text='Retrieve Image', font=('Montserrat', 14, 'bold'), 
                                   fg='#00FF00', bg='#0c0c0c', width=15, cursor='hand2', command=self.retrieve_from_database)
        self.canvas.create_window(self.canvas_width // 0.69, self.canvas_height // 1.0, window=self.retrieve_image)


        self.image_data_list = []
        self.current_index = -1  

        self.fname_entry.insert(0, 'First Name')
        self.mname_entry.insert(0, 'MI (Optional)')
        self.lname_entry.insert(0, 'Last Name')
        self.contact_entry.insert(0, 'Contact Number')
        self.city_entry.insert(0, 'City')
        self.province_entry.insert(0, 'Province')
        self.email_entry.insert(0, 'Email')
        self.pass_entry.insert(0, 'Password')
        self.confirm_pass_entry.insert(0, 'Confirm Password')

        self.crop_canvas = None
        self.crop_rect = None
        self.crop_start = None

        self.bind()

    def upload_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.original_image = Image.open(file_path)
            self.original_image = self.original_image.resize((200, 200), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(self.original_image)
            self.image_label.config(image=self.photo)
            self.image_label.image = self.photo
    def start_crop(self):
        if not hasattr(self, 'original_image'):
            messagebox.showerror("Error", "Please upload an image first.")
            return

        self.top = tk.Toplevel(self)
        self.top.title("Crop Image")

        self.crop_canvas = tk.Canvas(self.top, width=self.original_image.width, height=self.original_image.height)
        self.crop_canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.crop_canvas.pack()
        self.crop_canvas.bind("<Button-1>", self.on_crop_start)
        self.crop_canvas.bind("<B1-Motion>", self.on_crop_drag)
        self.crop_canvas.bind("<ButtonRelease-1>", self.on_crop_end)

        self.crop_rect = None
        self.crop_start = None

    def on_crop_start(self, event):
        self.crop_start = (event.x, event.y)
        if self.crop_rect:
            self.crop_canvas.delete(self.crop_rect)

    def on_crop_drag(self, event):
        if self.crop_rect:
            self.crop_canvas.delete(self.crop_rect)
        x0, y0 = self.crop_start
        x1, y1 = event.x, event.y
        self.crop_rect = self.crop_canvas.create_rectangle(x0, y0, x1, y1, outline="red")

    def on_crop_end(self, event):
        if self.crop_rect:
            self.crop_canvas.delete(self.crop_rect)
        x0, y0 = self.crop_start
        x1, y1 = event.x, event.y

        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        self.cropped_image = self.original_image.crop((x0, y0, x1, y1))
        self.cropped_image = self.cropped_image.resize((200, 200), Image.LANCZOS)
        self.crop_photo = ImageTk.PhotoImage(self.cropped_image)
        self.image_label.config(image=self.crop_photo)
        self.image_label.image = self.crop_photo
        self.crop_canvas.destroy()
        self.top.destroy()

    def validate_input(self, text):
        regex = "^[A-Za-z ]+$"
        if re.match(regex, text):
            return True
        else:
            return False
        
    def onclick_create(self):
        fname = self.fname_entry.get()
        mname = self.mname_entry.get()
        lname = self.lname_entry.get()
        contact = self.contact_entry.get()
        city = self.city_entry.get()
        province = self.province_entry.get()
        email = self.email_entry.get()
        password = self.pass_entry.get()
        confirm_password = self.confirm_pass_entry.get()

        if fname == 'First Name'or lname == 'Last Name' or contact == 'Contact Number' or city == 'City' or province == 'Province' or email == 'Email' or confirm_password == 'Confirm Password':
            messagebox.showerror('Error', 'Please fill all the fields')
            return
        elif password == 'Password' or password == 'password':
            messagebox.showerror('Error', 'Password must be unique')
            return
        elif password != confirm_password:
            messagebox.showerror('Error', 'Passwords do not match')
            return
        elif not self.validate_input(fname):
            messagebox.showerror('Error', 'First Name must contain only letters')
            return
        elif not self.validate_input(mname):
            if mname == 'MI (Optional)':
                mname = 'N/A'
            elif not mname.strip():
                mname = 'N/A'
            else:
                messagebox.showerror('Error', 'Middle Name must contain only letters')
                return
        elif not self.validate_input(lname):
            messagebox.showerror('Error', 'Last Name must contain only letters')
            return
        elif not contact.replace("+", "").replace(" ", "").isdigit():
            messagebox.showerror('Error', 'Contact Number must contain only numbers')
            return
        elif not self.validate_input(city):
            messagebox.showerror('Error', 'City must contain only letters')
            return
        elif not self.validate_input(province):
            messagebox.showerror('Error', 'Province must contain only letters')
            return
        if len(contact) != 13:
            messagebox.showerror('Error', 'Contact Number must be 13 digits')
            return
        elif len(password) <= 5:
            messagebox.showerror('Error', 'Password must be at least 6 characters')
            return
            
        profile = models.Profiles()
        profile.fname = fname
        profile.mname = mname
        profile.lname = lname
        profile.contact = contact
        profile.city = city
        profile.province = province
        profile.email = email
        profile.password = password

        if hasattr(self, 'cropped_image'):
            with io.BytesIO() as buffer:
                self.cropped_image.save(buffer, format='PNG')
                image_data_cropped = buffer.getvalue()
                profile.image_data = image_data_cropped
                db_conn = db_handler.DBHandler()            
                db_conn.insert_account(profile)
                db_conn.close()
                messagebox.showinfo('Successfully Created', f'Welcome {fname}')
                self.parent.change_frame('LoginPage')
        elif hasattr(self, 'original_image'):
            with io.BytesIO() as buffer:
                self.original_image.save(buffer, format='PNG')
                image_data_orig = buffer.getvalue()
                profile.image_data = image_data_orig
                db_conn = db_handler.DBHandler()            
                db_conn.insert_account(profile)
                db_conn.close()
                messagebox.showinfo('Successfully Created', f'Welcome {fname}')
                self.parent.change_frame('LoginPage')
        else:
            messagebox.showerror("Error", "No Image to save.")

            
    def retrieve_from_database(self):
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT image FROM profiles")
        self.image_data_list = self.cursor.fetchall()
        if self.image_data_list:
            self.current_index = (self.current_index + 1) % len(self.image_data_list)
            image_data = self.image_data_list[self.current_index][0]
            image = Image.open(io.BytesIO(image_data))
            image = image.resize((200, 200), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo
            print("Image retrieved from database.")
        else:
            print("No images found in the database.")

    def bind(self):
        self.fname_entry.bind('<FocusIn>', self.fname_entry_enter)
        self.fname_entry.bind('<FocusOut>', self.fname_entry_leave)
        self.lname_entry.bind('<FocusIn>', self.lname_entry_enter)
        self.lname_entry.bind('<FocusOut>', self.lname_entry_leave)
        self.mname_entry.bind('<FocusIn>', self.mname_entry_enter)
        self.mname_entry.bind('<FocusOut>', self.mname_entry_leave)
        self.email_entry.bind('<FocusIn>', self.email_entry_enter)
        self.email_entry.bind('<FocusOut>', self.email_entry_leave)
        self.pass_entry.bind('<FocusIn>', self.pass_entry_enter)
        self.pass_entry.bind('<FocusOut>', self.pass_entry_leave)
        self.confirm_pass_entry.bind('<FocusIn>', self.confirm_pass_entry_enter)
        self.confirm_pass_entry.bind('<FocusOut>', self.confirm_pass_entry_leave)
        self.canvas.bind('<Button-1>', self.canvas_clicked)
        self.contact_entry.bind('<FocusIn>', self.contact_entry_enter)
        self.contact_entry.bind('<FocusOut>', self.contact_entry_leave)
        self.city_entry.bind('<FocusIn>', self.city_entry_enter)
        self.city_entry.bind('<FocusOut>', self.city_entry_leave)
        self.province_entry.bind('<FocusIn>', self.province_entry_enter)
        self.province_entry.bind('<FocusOut>', self.province_entry_leave)
        self.back_button.bind('<Button-1>', self.onclick_back)

    def onclick_back(self, event):
        fname = self.fname_entry.get()
        mname = self.mname_entry.get()
        lname = self.lname_entry.get()
        contact = self.contact_entry.get()
        city = self.city_entry.get()
        province = self.province_entry.get()
        email = self.email_entry.get()
        password = self.pass_entry.get()
        confirm_password = self.confirm_pass_entry.get()

        if  fname == 'First Name' and mname == 'MI (Optional)' and lname == 'Last Name' and contact == 'Contact Number' and city == 'City' and province == 'Province' and email == 'Email' and password == 'Password' and confirm_password == 'Confirm Password':
            self.parent.change_frame('LoginPage')
        elif fname or mname or lname or contact or city or province or email or password or confirm_password:
            confirmed = messagebox.askyesno('Warning', 'Are you sure you want to cancel?')
            if not confirmed:
                return
            else:
                self.parent.change_frame('LoginPage')
        else:
            return
        self.back_button.config(bg='#323232')

    def confirm_email_otp(self):
        pop_up_frame = tk.Toplevel(self)
        pop_up_frame.title('Confirm Email')


    def city_entry_enter(self, event):
        if self.city_entry.get() == 'City':
            self.city_entry.delete(0, tk.END)
            self.city_entry.insert(0, '')
    
    def city_entry_leave(self, event):
        if self.city_entry.get() == '':
            self.city_entry.delete(0, tk.END)
            self.city_entry.insert(0, 'City')

    def province_entry_enter(self, event):
        if self.province_entry.get() == 'Province':
            self.province_entry.delete(0, tk.END)
            self.province_entry.insert(0, '')

    def province_entry_leave(self, event):
        if self.province_entry.get() == '':
            self.province_entry.delete(0, tk.END)
            self.province_entry.insert(0, 'Province')

    def contact_entry_enter(self, event):
        if self.contact_entry.get() == 'Contact Number':
            self.contact_entry.delete(0, tk.END)
            self.contact_entry.insert(0, '+63')
            
    def contact_entry_leave(self, event):
        if self.contact_entry.get() == '' or self.contact_entry.get() == '+63':
            self.contact_entry.delete(0, tk.END)
            self.contact_entry.insert(0, 'Contact Number')
    
    def confirm_pass_entry_enter(self, event):
        if self.confirm_pass_entry.get() == 'Confirm Password':
            self.confirm_pass_entry.delete(0, tk.END)
            self.confirm_pass_entry.insert(0, '')
            self.confirm_pass_entry.config(show='*')
    
    def confirm_pass_entry_leave(self, event):
        if self.confirm_pass_entry.get() == '':
            self.confirm_pass_entry.delete(0, tk.END)
            self.confirm_pass_entry.insert(0, 'Confirm Password')
            self.confirm_pass_entry.config(show='')

    def email_entry_leave(self, event):
        if self.email_entry.get() == '':
            self.email_entry.delete(0, tk.END)
            self.email_entry.insert(0, 'Email')
    
    def email_entry_enter(self, event):
        if self.email_entry.get() == 'Email':
            self.email_entry.delete(0, tk.END)
            self.email_entry.insert(0, '')

    def mname_entry_enter(self, event):
        if self.mname_entry.get() == 'MI (Optional)':
            self.mname_entry.delete(0, tk.END)
            self.mname_entry.insert(0, '')
    
    def mname_entry_leave(self, event):
        if self.mname_entry.get() == '':
            self.mname_entry.delete(0, tk.END)
            self.mname_entry.insert(0, 'MI (Optional)')

    def lname_entry_leave(self, event):
        if self.lname_entry.get() == '':
            self.lname_entry.delete(0, tk.END)
            self.lname_entry.insert(0, 'Last Name')

    def lname_entry_enter(self, event):
        if self.lname_entry.get() == 'Last Name':
            self.lname_entry.delete(0, tk.END)
            self.lname_entry.insert(0, '')

    def fname_entry_enter(self, event):
        if self.fname_entry.get() == 'First Name':
            self.fname_entry.delete(0, tk.END)
            self.fname_entry.insert(0, '')
            

    def fname_entry_leave(self, event):
        if self.fname_entry.get() == '' :
            self.fname_entry.delete(0, tk.END)
            self.fname_entry.insert(0, 'First Name')
            
        
    def pass_entry_enter(self, event):
        if self.pass_entry.get() == 'Password':
            self.pass_entry.delete(0, tk.END)
            self.pass_entry.insert(0, '')
            self.pass_entry.config(show='*')
    
    def pass_entry_leave(self, event):
        if self.pass_entry.get() == '':
            self.pass_entry.delete(0, tk.END)
            self.pass_entry.insert(0, 'Password')
            self.pass_entry.config(show='')

    def canvas_clicked(self, event):
        self.focus_set()

    def onclick(self, event):
        self.parent.change_frame('LoginPage')

class LandingPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        self.master.title('Landing Page')
        self.label = tk.Label(self, text='LANDING PAGE')
        self.label.grid(row=0, column=0)
        

class AdminPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        self.master.title('Admin Page')
        self.label = tk.Label(self, text='ADMIN PAGE')
        self.label.grid(row=0, column=0)
