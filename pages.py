import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import filedialog, simpledialog
from PIL import Image, ImageTk, ImageOps, ImageEnhance, ImageFilter
from tkinter import messagebox
from random import randint
from email.message import EmailMessage
from captcha.image import ImageCaptcha
import ssl
import smtplib
# import sqlite3
import db_handler
import models
import re
import io
import os
import string
import random

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
        self.parent.title('Login')
        self.config(background='black')
        master.minsize(width=787, height=461)
        master.bind('<Unmap>', self.on_minimize)
        master.bind('<Map>', self.on_restore)
        self.create_labels()
        self.show_canvas()
    def on_minimize(self, event):
        self.parent.geometry("787x461")

    def on_restore(self, event):
        self.parent.geometry("787x461")
    def create_labels(self):
        labels = []
        for i in range(11):
            for j in range(19):
                label = FadingLabel(self, text="", width=10, height=4, background="#121212")
                label.grid(row=i, column=j, padx=2, pady=2, ipadx=1, ipady=1)
                labels.append(label)
                label.bind('<Button-1>', self.focusSet)

    def focusSet(self, event):
        self.focus_set()

    def show_canvas(self):
        self.canvas_width = 600
        self.canvas_height = 500
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg='#0c0c0c', 
                                highlightbackground='#00FF00', highlightthickness=4)
        self.canvas.grid(row=1, column=4, rowspan=9, columnspan=11, sticky='nsew')
        self.canvas.config(highlightbackground='#00FF00')
        for i in range(11):
            self.grid_rowconfigure(i, weight=1)
        for j in range(19):  
            self.grid_columnconfigure(j, weight=1)
        self.show_object()

    def show_object(self):
        self.sign_in_lb = tk.Label(self, text="SIGN IN", font=("Montserrat", 40, "bold"),
                                     fg='#00FF00', bg='#0c0c0c', highlightbackground='#00FF00')
        self.sign_in_lb.place(relx=0.5, rely=0.2, anchor='center')

        self.entry_email = tk.Entry(self, font=('Monospac821 BT', 17), width=30, justify='center', fg='white', bg='#323232')
        self.entry_email.place(relx=0.5, rely=0.35, anchor='center')
        self.entry_email.insert(0, 'Email')
        

        self.entry_pass = tk.Entry(self, font=('Monospac821 BT', 17), width=30, justify='center', fg='white', bg='#323232')
        self.entry_pass.place(relx=0.5, rely=0.45, anchor='center')
        self.entry_pass.insert(0, 'Password')

        self.login_btn = tk.Button(self, text='LOGIN', font=('Montserrat', 17, 'bold'), 
                                   fg='#00FF00', bg='#0c0c0c', width=25, cursor='hand2', command=self.onclick_login)
        self.login_btn.place(relx=0.5, rely=0.59, anchor='center')

        self.forgot_pass_label = tk.Label(self, text='Forgot Password', font=('Monospac821 BT', 11, 'underline'), 
                                          bg='#0c0c0c', fg='white', cursor='hand2')
        self.forgot_pass_label.place(relx=0.4, rely=0.7, anchor='center')

        self.signup_label = tk.Label(self, text='SIGN-UP', font=('Monospac821 BT', 11), bg='#0c0c0c', fg='#00FF00', cursor='hand2')
        self.signup_label.place(relx=0.62, rely=0.7, anchor='center')
        self.canvas.focus_set
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
        
        else:
            messagebox.showerror("Invalid Login", "Invalid username or password")
            return
        

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
        self.parent.title('Sign Up')
        master.minsize(width=1062, height=638)
        master.bind('<Unmap>', self.on_minimize_signup)
        master.bind('<Map>', self.on_restore_signup)
        self.config(background='black')
        self.original_image = None
        self.create_labels()
        self.show_canvas()

    def on_minimize_signup(self, event):
        self.parent.geometry("1062x638")

    def on_restore_signup(self, event):
        self.parent.geometry("1062x638")

    def create_labels(self):
        labels = []
        for i in range(11):
            for j in range(19):
                label = FadingLabel(self, text="", width=10, height=4, background="#121212")
                label.grid(row=i, column=j, padx=2, pady=2, ipadx=1, ipady=1)
                labels.append(label)

    def show_canvas(self):
        self.canvas_width = 600
        self.canvas_height = 500
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg='#0c0c0c', highlightbackground='#00FF00', highlightthickness=2)
        self.canvas.grid(row=1, column=2, rowspan=9, columnspan=15, sticky='nsew')
        for i in range(11):
            self.grid_rowconfigure(i, weight=1)
        for j in range(19):  
            self.grid_columnconfigure(j, weight=1)
        self.show_object()

    def show_object(self):
        self.chk_box_var = tk.BooleanVar()
        
        self.label = tk.Label(self.canvas, text='Create Account', font=('Montserrat', 25, 'bold'), fg='#00FF00', bg='#0c0c0c')
        self.label.place(relx=0.5, rely=0.02, anchor='n')

        self.personal_label = tk.Label(self, text='Personal Info', font=('Monospac821 BT', 11), fg='#00FF00', bg='#0c0c0c')
        self.personal_label.place(relx=0.15, rely=0.21, anchor='w')

        self.fname_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=20, justify='center', fg='white', bg='#323232')
        self.fname_entry.place(relx=0.25, rely=0.28, anchor='center')
        
        self.mname_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=20, justify='center', fg='white', bg='#323232')
        self.mname_entry.place(relx=0.25, rely=0.36, anchor='center')

        self.lname_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=20, justify='center', fg='white', bg='#323232')
        self.lname_entry.place(relx=0.25, rely=0.44, anchor='center')

        self.other_label = tk.Label(self, text='Other Info', font=('Monospac821 BT', 11), fg='#00FF00', bg='#0c0c0c')
        self.other_label.place(relx=0.15, rely=0.54, anchor='w')

        self.contact_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=20, justify='center', fg='white', bg='#323232')
        self.contact_entry.place(relx=0.25, rely=0.6, anchor='center')

        self.city_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=20, justify='center', fg='white', bg='#323232')
        self.city_entry.place(relx=0.25, rely=0.68, anchor='center')

        self.province_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=20, justify='center', fg='white', bg='#323232')
        self.province_entry.place(relx=0.25, rely=0.77, anchor='center')

        self.account_label = tk.Label(self, text='Account Info', font=('Monospac821 BT', 11), fg='#00FF00', bg='#0c0c0c')
        self.account_label.place(relx=0.37, rely=0.21, anchor='w')

        self.email_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=30, justify='center', fg='white', bg='#323232')
        self.email_entry.place(relx=0.505, rely=0.28, anchor='center')

        self.pass_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=30, justify='center', fg='white', bg='#323232')
        self.pass_entry.place(relx=0.505, rely=0.36, anchor='center')

        self.confirm_pass_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=30, justify='center', fg='white', bg='#323232')
        self.confirm_pass_entry.place(relx=0.505, rely=0.44, anchor='center')

        self.terms_condition_lb = tk.Label(self, text='Terms & Conditions', font=('Monospac821 BT', 11), fg='#00FF00', bg='#0c0c0c')
        self.terms_condition_lb.place(relx=0.4, rely=0.48, anchor='w')
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
        self.text_box_terms_conditions.config(state=tk.DISABLED)
        self.text_box_terms_conditions.place(relx=0.505, rely=0.57, anchor='center')

        self.chk_btn = tk.Checkbutton(self, text='Agree to terms', variable=self.chk_box_var, fg='#00FF00', bg='#0c0c0c', font=('Monospac821 BT', 10))
        self.chk_btn.place(relx=0.505, rely=0.68, anchor='center')

        self.create_btn = tk.Button(self, text='Create Account', font=('Montserrat', 14, 'bold'), 
                                   fg='#00FF00', bg='#0c0c0c', width=15, cursor='hand2', command=self.onclick_create)
        self.create_btn.place(relx=0.505, rely=0.75, anchor='center')

        self.back_image_path = 'back.png'
        self.pil_image_back_image = Image.open(self.back_image_path)
        self.resize_back_image = self.pil_image_back_image.resize((30,30))
        self.image_back_image = ImageTk.PhotoImage(self.resize_back_image)
        self.back_button = tk.Label(self, image=self.image_back_image, bg='#0c0c0c', cursor='hand2')
        self.back_button.place(relx=0.85, rely=0.15, anchor='center')

        self.image_label = tk.Label(self, text='No Image Uploaded', font=('Monospac821 BT', 12), fg='#00FF00', bg='#0c0c0c', cursor='hand2', image='')
        self.image_label.place(relx=0.67, rely=0.4, anchor='w')

        self.crop_btn = tk.Button(self, text='Crop', font=('Montserrat', 14, 'bold'), 
                                   fg='#00FF00', bg='#0c0c0c', width=15, cursor='hand2', command=self.start_crop)
        self.crop_btn.place(relx=0.67, rely=0.6, anchor='w')

        self.upload_btn = tk.Button(self, text='Upload Image', font=('Montserrat', 14, 'bold'), 
                                   fg='#00FF00', bg='#0c0c0c', width=15, cursor='hand2', command=self.upload_image)
        self.upload_btn.place(relx=0.67, rely=0.7, anchor='w')

        self.filter_options = ["Select Filter","Original", "Grayscale", "Blur", "Sharpen",
                              "Contour", "Edge Enhance", "Emboss", "Smooth", "Brightness", "Contrast"]
        self.filter_var = tk.StringVar()
        self.filter_var.set(self.filter_options[0])

        self.filter_menu = tk.OptionMenu(self, self.filter_var, *self.filter_options, command=self.apply_filter)
        self.filter_menu.config(bg='#0c0c0c', fg='#00FF00', font=('Monospac821 BT', 14), width=15, highlightbackground='#0c0c0c', highlightthickness=1)
        self.filter_menu.place(relx=0.67, rely=0.8, anchor='w')

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

    def apply_filter(self, filter_option):
        if self.image_label.cget('image') is None:
            messagebox.showerror("Error", "Please load an image first.")
            return
        if self.original_image is None:
            messagebox.showerror("Error", "Please load an image first.")
            return
        try:
            if filter_option == "Original":
                self.filtered_image = self.original_image.copy()
            else:
                if filter_option == "Grayscale":
                    self.filtered_image = self.original_image.convert("L")
                elif filter_option == "Blur":
                    self.filtered_image = self.original_image.filter(ImageFilter.BLUR)
                elif filter_option == "Sharpen":
                    self.filtered_image = self.original_image.filter(ImageFilter.SHARPEN)
                elif filter_option == "Contour":
                    self.filtered_image = self.original_image.filter(ImageFilter.CONTOUR)
                elif filter_option == "Edge Enhance":
                    self.filtered_image = self.original_image.filter(ImageFilter.EDGE_ENHANCE)
                elif filter_option == "Emboss":
                    self.filtered_image = self.original_image.filter(ImageFilter.EMBOSS)
                elif filter_option == "Smooth":
                    self.filtered_image = self.original_image.filter(ImageFilter.SMOOTH)
                elif filter_option == "Brightness":
                    enhancer = ImageEnhance.Brightness(self.original_image)
                    self.filtered_image = enhancer.enhance(1.5)
                elif filter_option == "Contrast":
                    enhancer = ImageEnhance.Contrast(self.original_image)
                    self.filtered_image = enhancer.enhance(1.5)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply filter: {e}")
        if self.filtered_image is None:
            messagebox.showerror("Error", "Failed to apply filter.")
            return

        self.photo = ImageTk.PhotoImage(self.filtered_image)
        self.image_label.config(image=self.photo)
        self.image_label.image = self.photo

    def upload_image(self, event=None):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            self.original_image = Image.open(file_path)
            self.original_image = self.original_image.resize((200, 200), Image.LANCZOS)
            self.filtered_image = self.original_image.copy()
            self.photo = ImageTk.PhotoImage(self.original_image)
            self.image_label.config(image=self.photo)
            self.image_label.image = self.photo
    def start_crop(self):
        if not hasattr(self, 'original_image'):
            messagebox.showerror("Error", "Please upload an image first.")
            return

        self.top = tk.Toplevel(self)
        self.top.title("Crop Image")
        self.top.resizable(False, False)
        if hasattr(self, 'original_image'):
            self.crop_canvas = tk.Canvas(self.top, width=self.original_image.width, height=self.original_image.height)
            self.crop_canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        elif hasattr(self, 'filtered_image'):
            self.crop_canvas = tk.Canvas(self.top, width=self.filtered_image.width, height=self.filtered_image.height)
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

        if hasattr(self, 'filtered_image'):
            self.filtered_image = self.filtered_image.crop((x0, y0, x1, y1))
            self.filtered_image = self.filtered_image.resize((200, 200), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(self.filtered_image)
            self.image_label.config(image=self.photo)
            self.image_label.image = self.photo
        else:
            self.original_image = self.original_image.crop((x0, y0, x1, y1))
            self.original_image = self.original_image.resize((200, 200), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(self.original_image)
            self.image_label.config(image=self.photo)
            self.image_label.image = self.photo

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

        if self.chk_box_var.get() == 0:
            messagebox.showwarning('Terms & Conditions', 'Terms & condition is unchecked')
            return
        
        if not hasattr(self, 'original_image'):
            messagebox.showerror("Error", "Please upload an image first.")
            return
        elif '@gmail.com' not in email:
            messagebox.showerror("Error", "Please enter a valid Gmail address.")
            return


        self.confirm_email_otp()

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
        self.image_label.bind('<Button-1>', self.upload_image)

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
        self.pop_up_frame = tk.Toplevel(self)
        self.pop_up_frame.title('Confirm Email')
        self.pop_up_frame.geometry('600x530')
        self.pop_up_frame.grab_set()
        self.pop_up_frame.focus_set()
        self.pop_up_frame.config(background='black')
        self.pop_up_frame.resizable(width=False, height=False)
        

        fname = self.fname_entry.get()
        mname = self.mname_entry.get()
        lname = self.lname_entry.get()
        contact = self.contact_entry.get()
        city = self.city_entry.get()
        province = self.province_entry.get()
        email = self.email_entry.get()
        password = self.pass_entry.get()
        
        otp_code = ''

        def send_email():
            emailSender = 'receiver.not404@gmail.com'
            emailPassword = 'yhwb ijon zrxw hpzj'
            emailReceiver = email

            subject = 'One-Time-Password'
            body = f"""
            Your One Time Password (OTP) for account verification is: {otp_code}. 
            Please use this OTP to complete your registration process. Do not share this OTP with anyone for security reasons
            """

            em = EmailMessage()

            em['From'] = emailSender
            em['To'] = emailReceiver
            em['Subject'] = subject
            em.set_content(body)


            context = ssl.create_default_context()

            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(emailSender, emailPassword)
                smtp.sendmail(emailSender, emailReceiver, em.as_string())
        def generate_otp():
            nonlocal otp_code
            otp_code = ''.join(str(randint(0, 9)) for _ in range(6))
            send_email()
        generate_otp()


        labels = []
        for i in range(10):
            for j in range(20):
                label = FadingLabel(self.pop_up_frame, text="", width=10, height=4, background="#121212")
                label.grid(row=i, column=j, padx=2, pady=2, ipadx=1, ipady=1)
                labels.append(label)

        self.canvas_width = 300
        self.canvas_height = 200
        self.canvas = tk.Canvas(self.pop_up_frame, width=self.canvas_width, height=self.canvas_height, bg='#0c0c0c', highlightbackground='#00FF00', highlightthickness=2)
        self.canvas.grid(row=1, column=1, rowspan=5, columnspan=5, sticky='nsew')

        self.label = tk.Label(self.pop_up_frame, text='OTP has been sent to your Email', font=('Monospac821 BT', 15, 'bold'), fg='#00FF00', bg='#0c0c0c')
        self.canvas.create_window(self.canvas_width // 1.4, self.canvas_height // 5, window=self.label)

        self.otp_entry = tk.Entry(self.pop_up_frame, font=('Monospac821 BT', 14), width=20, justify='center', fg='white', bg='#323232')
        self.canvas.create_window(self.canvas_width // 1.4, self.canvas_height // 2, window=self.otp_entry)

        remaining_time = 180

        self.resend_lb = tk.Label(self.pop_up_frame, text="", font=('Monospac821 BT', 10, 'bold'), fg='#00FF00', bg='#0c0c0c')
        self.canvas.create_window(self.canvas_width // 1.4, self.canvas_height // 1.5, window=self.resend_lb)

        def  generate_captcha(text_length = 6, folder = 'captcha'):
            characters = string.ascii_letters + string.digits
            captcha_text = ''.join(random.choices(characters, k=text_length))
            captcha = ImageCaptcha()
            if not os.path.exists(folder):
                os.makedirs(folder)
            captcha_image_file = os.path.join(folder, f'{captcha_text}.png')
            captcha.write(captcha_text, captcha_image_file)
            return captcha_text, captcha_image_file
        
        def check_captcha(user_input, captcha_text):
            return user_input == captcha_text

        def delete_captcha(captcha_image_file):
            os.remove(captcha_image_file)
            print("CAPTCHA image deleted successfully!")

        def generate_new_captcha():
            nonlocal captcha_text, captcha_image_file

            if os.path.exists(captcha_image_file):
                os.remove(captcha_image_file)
                print("Previous CAPTCHA image deleted successfully!")

            captcha_text, captcha_image_file = generate_captcha()
            new_captcha_image = Image.open(captcha_image_file)
            new_captcha_image_tk = ImageTk.PhotoImage(new_captcha_image)
            captcha_label.configure(image=new_captcha_image_tk)
            captcha_label.image = new_captcha_image_tk

        captcha_text, captcha_image_file = generate_captcha()
        captcha_image = Image.open(captcha_image_file)
        captcha_image_tk = ImageTk.PhotoImage(captcha_image)
        captcha_label = tk.Label(self.pop_up_frame, image=captcha_image_tk)
        captcha_label.image = captcha_image_tk
        self.canvas.create_window(self.canvas_width // 1.4, self.canvas_height // 0.85, window=captcha_label)

        generate_button = tk.Button(self.pop_up_frame, text="Generate New CAPTCHA", font=('Montserrat', 8, 'bold'), 
                                fg='#00FF00', bg='#0c0c0c', width=20, cursor='hand2', command=generate_new_captcha)
        self.canvas.create_window(self.canvas_width // 1.4, self.canvas_height // 0.68, window=generate_button)

        captcha_entry = tk.Entry(self.pop_up_frame, font=('Monospac821 BT', 14), width=20, justify='center', fg='white', bg='#323232')
        self.canvas.create_window(self.canvas_width // 1.4, self.canvas_height // 0.6, window=captcha_entry)

        def validate_input(text):
            regex = "^[A-Za-z ]+$"
            if re.match(regex, text):
                return True
            else:
                return False
        
        def upload_data_to_db():
            mname = self.mname_entry.get()
            profile = models.Profiles()
            profile.fname = fname
            profile.lname = lname
            profile.contact = contact
            profile.city = city
            profile.province = province
            profile.email = email
            profile.password = password

            entered_otp = self.otp_entry.get()

            if not validate_input(mname):
                if mname == 'MI (Optional)':
                    mname = 'N/A'
                elif not mname.strip():
                    mname = 'N/A'
                else:
                    messagebox.showerror('Error', 'Middle Name must contain only letters')
                    return
            profile.mname = mname
            if entered_otp != otp_code:
                messagebox.showerror('Error', 'OTP is wrong')
                return
            
            entered_captcha = captcha_entry.get()
            if not check_captcha(entered_captcha, captcha_text):
                messagebox.showerror('Error', 'Incorrect CAPTCHA')
                return
            delete_captcha(captcha_image_file)

            if hasattr(self, 'cropped_image'):
                image_to_save = self.cropped_image
            elif hasattr(self, 'filtered_image'):
                image_to_save = self.filtered_image
            elif hasattr(self, 'original_image'):
                image_to_save = self.original_image
            else:
                messagebox.showerror("Error", "No Image to save.")
                return

            with io.BytesIO() as buffer:
                image_to_save.save(buffer, format='PNG')
                image_data = buffer.getvalue()
                profile.image_data = image_data
                db_conn = db_handler.DBHandler()            
                db_conn.insert_account(profile)
                db_conn.close()
                messagebox.showinfo('Successfully Created', f'Welcome {profile.fname}')
                self.parent.change_frame('LoginPage')
            self.pop_up_frame.destroy()
            self.image_label.cget('text') == 'No Image Uploaded'
        self.confirm_otp_btn = tk.Button(self.pop_up_frame, text='Confirm OTP', font=('Montserrat', 14, 'bold'), 
                                fg='#00FF00', bg='#0c0c0c', width=15, cursor='hand2', command='upload_data_to_db')
        self.canvas.create_window(self.canvas_width // 1.4, self.canvas_height // 1.2, window=self.confirm_otp_btn)

        def update_label():
            nonlocal remaining_time
            nonlocal otp_code
            self.confirm_otp_btn.config(text='Confirm OTP')
            self.confirm_otp_btn.config(command=upload_data_to_db)
            if remaining_time <= 0:
                self.resend_lb.config(text="Time's up!")
                self.confirm_otp_btn.config(text='Resend OTP')
                self.confirm_otp_btn.config(command=repeat_clock)
            else:
                self.resend_lb.config(text=f"Resend in: {remaining_time} seconds")
                remaining_time -= 1
                self.pop_up_frame.after(1000, update_label)

        def repeat_clock():
            nonlocal remaining_time
            remaining_time = 180
            update_label()
            generate_otp()

        update_label()

        def on_window_destroy(event):
            captcha_folder = 'captcha'
            for file_name in os.listdir(captcha_folder):
                file_path = os.path.join(captcha_folder, file_name)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                        print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
        self.pop_up_frame.bind("<Destroy>", on_window_destroy)

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

class ForgotPassword(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        self.master.title('Forgot Password')
        self.label = tk.Label(self, text='Forgot Password')
        self.label.grid(row=0, column=0)



