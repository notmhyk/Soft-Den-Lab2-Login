import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, simpledialog, messagebox
from PIL import Image, ImageTk, ImageOps, ImageEnhance, ImageFilter
from random import randint
import random
from email.message import EmailMessage
from captcha.image import ImageCaptcha
import ssl, smtplib, db_handler, models, re, io, os, string
import _tkinter

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
        
        if email == 'Email':
            messagebox.showerror('Error', 'Email cannot be empty')
            return
        elif password == 'Password':
            messagebox.showerror('Error', 'Password cannot be empty')
            return
        
        if self.parent.db_handler.acc_login(email, password):
            self.parent.change_frame('LandingPage', email=email)
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
        self.forgot_pass_label.bind('<Button-1>', self.on_click_forgot_pass)

    def on_click_forgot_pass(self, event):
        self.parent.change_frame('ForgotPassword')

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
    def __init__(self, master=None):
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
        self.after(4000, self.center_option_menus)
        

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

        self.gender_options = ["Gender","Male", "Female", "Others"]
        self.gender_var = tk.StringVar()
        self.gender_var.set(self.gender_options[0])

        self.gender = tk.OptionMenu(self, self.gender_var, *self.gender_options)
        self.gender.config(bg='#0c0c0c', fg='#00FF00', font=('Monospac821 BT', 12), width=15, highlightbackground='#0c0c0c', highlightthickness=1)
        self.gender.place(relx=0.18, rely=0.6, anchor='w')

        self.city_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=20, justify='center', fg='white', bg='#323232')
        self.city_entry.place(relx=0.25, rely=0.68, anchor='center')

        self.province_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=20, justify='center', fg='white', bg='#323232')
        self.province_entry.place(relx=0.25, rely=0.77, anchor='center')

        self.marital_status_options = [
            "Status",
            "Single",
            "Married",
            "Widowed",
            "Divorced",
            "Separated",
            "Annulled",
            "In a Relationship",
            "Other"]
        self.marital_status_var = tk.StringVar()
        self.marital_status_var.set(self.marital_status_options[0])
        self.marital_status_menu = tk.OptionMenu(self, self.marital_status_var, *self.marital_status_options)
        self.marital_status_menu.config(bg='#0c0c0c', fg='#00FF00', font=('Monospac821 BT', 12), width=17, highlightbackground='#0c0c0c', highlightthickness=1)
        self.marital_status_menu.place(relx=0.175, rely=0.85, anchor='w')

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

        self.bind_validation(self.fname_entry)
        self.bind_validation(self.lname_entry)
        self.bind_validation(self.city_entry)
        self.bind_validation(self.province_entry)
        
    
        self.fname_entry.insert(0, 'First Name')
        self.mname_entry.insert(0, 'Middle Initial')
        self.lname_entry.insert(0, 'Last Name')
        self.city_entry.insert(0, 'City')
        self.province_entry.insert(0, 'Province')
        self.email_entry.insert(0, 'Email')
        self.pass_entry.insert(0, 'Password')
        self.confirm_pass_entry.insert(0, 'Confirm Password')

        self.crop_canvas = None
        self.crop_rect = None
        self.crop_start = None
        self.master.bind("<Configure>", self.center_option_menus)
        self.bind()
    def center_option_menus(self, event=None):
        try:
            if event:
                window_width = self.winfo_width()
            else:
                window_width = self.parent.winfo_width() 

            marital_status_width = self.marital_status_menu.winfo_reqwidth()
            marital_status_x = (window_width * 0.078) - (marital_status_width / 2)

            gender_width = self.gender.winfo_reqwidth()
            gender_x = (window_width * 0.075) - (gender_width / 2)

            self.marital_status_menu.place(x=marital_status_x, rely=0.85, anchor='w')
            self.gender.place(x=gender_x, rely=0.6, anchor='w')
        except _tkinter.TclError as e:
            # print("An error occurred:", e)
            pass

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
        if self.original_image is None:
            messagebox.showerror("Error", "Please load an image first.")
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
        regex = "^[A-Za-z ]*$"
        return re.match(regex, text) is not None
    
    def validate_mname(self, text):
        return len(text) <= 1 and self.validate_input(text)
    
    def bind_validation(self, entry, validate_func=None):
        entry.config(validate="key")
        if validate_func:
            entry.config(validatecommand=(self.register(validate_func), "%P"))
        else:
            entry.config(validatecommand=(self.register(self.validate_input), "%P"))

    def onclick_create(self):
        
        fname = self.fname_entry.get()
        mname = self.mname_entry.get()
        lname = self.lname_entry.get()
        gender = self.gender_var.get()
        city = self.city_entry.get()
        province = self.province_entry.get()
        status = self.marital_status_var.get()
        email = self.email_entry.get()
        password = self.pass_entry.get()
        confirm_password = self.confirm_pass_entry.get()

        if fname == 'First Name'or lname == 'Last Name' or gender == 'Gender' or city == 'City' or province == 'Province' or status == 'Status' or email == 'Email' or confirm_password == 'Confirm Password':
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
            if mname == 'Middle Initial':
                mname = ''
            elif not mname.strip():
                mname = ''
            else:
                messagebox.showerror('Error', 'Middle Initial must contain only letters')
                return
        elif not self.validate_input(lname):
            messagebox.showerror('Error', 'Last Name must contain only letters')
            return
        
        if self.gender_var.get() == "Gender":
            messagebox.showerror('Error', 'Please select gender')
            return
        
        if self.marital_status_var.get() == "Status":
            messagebox.showerror('Error', 'Please select marital status')
            return

        if not city.replace(" ", "").isalpha():
            messagebox.showerror('Error', 'City must contain only letters')
            return
        
        if not province.replace(" ", "").isalpha():
            messagebox.showerror('Error', 'Province must contain only letters')
            return
        
        if len(password) <= 5:
            messagebox.showerror('Error', 'Password must be at least 6 characters')
            return
        
        
        if self.chk_box_var.get() == 0:
            messagebox.showwarning('Terms & Conditions', 'Terms & condition is unchecked')
            return
        
        if not hasattr(self, 'original_image'):
            messagebox.showerror("Error", "Please upload an image first.")
            return
        
        if email.count('@') != 1 or not email.endswith('@gmail.com'):
            messagebox.showerror("Error", "Please enter a valid Gmail address.")
            return
        
        if mname == 'Middle Initial':
            mname = ''
        elif not mname.strip():
            mname = ''
        elif mname.isalpha():
            pass
        else:
            messagebox.showerror('Error', 'Middle Initial must contain only letterszz')
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
        gender = self.gender_var.get()
        city = self.city_entry.get()
        province = self.province_entry.get()
        status = self.marital_status_var.get()
        email = self.email_entry.get()
        password = self.pass_entry.get()
        confirm_password = self.confirm_pass_entry.get()

        if  fname == 'First Name' and mname == 'Middle Initial' and lname == 'Last Name' and gender == 'Gender' and city == 'City' and province == 'Province' and status == "Status" and email == 'Email' and password == 'Password' and confirm_password == 'Confirm Password':
            self.parent.change_frame('LoginPage')
        elif fname or mname or lname or gender or city or province or status or email or password or confirm_password:
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
        # contact = self.contact_entry.get()
        gender = self.gender_var.get()
        city = self.city_entry.get()
        province = self.province_entry.get()
        status = self.marital_status_var.get()
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

        def validate_input(text):
            return text.isdigit() or text == ""
        
        self.otp_entry = tk.Entry(self.pop_up_frame, font=('Monospac821 BT', 14), width=20, justify='center', fg='white', bg='#323232')
        self.canvas.create_window(self.canvas_width // 1.4, self.canvas_height // 2, window=self.otp_entry)

        self.otp_entry.config(validate="key")
        self.otp_entry.config(validatecommand=(self.register(validate_input), "%P"))

        remaining_time = 180

        self.resend_lb = tk.Label(self.pop_up_frame, text="", font=('Monospac821 BT', 10, 'bold'), fg='#00FF00', bg='#0c0c0c')
        self.canvas.create_window(self.canvas_width // 1.4, self.canvas_height // 1.5, window=self.resend_lb)

        def  generate_captcha(text_length = 3, folder = 'captcha'):
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

        def generate_new_captcha():
            nonlocal captcha_text, captcha_image_file

            if os.path.exists(captcha_image_file):
                os.remove(captcha_image_file)
                

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
        
        def upload_data_to_db():
            mname = self.mname_entry.get()
            profile = models.Profiles()
            profile.fname = fname
            profile.lname = lname
            profile.gender = gender
            profile.city = city
            profile.province = province
            profile.status = status
            profile.email = email
            profile.password = password

            entered_otp = self.otp_entry.get()

            if mname == 'Middle Initial':
                    mname = ''
            elif not mname.strip():
                mname = ''
            elif mname.isalpha():
                pass
            else:
                messagebox.showerror('Error', 'Middle Initial must contain only letters')
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
         if self.mname_entry.get() == 'Middle Initial':
            self.mname_entry.delete(0, tk.END)
            self.mname_entry.config(validate="key") 
            self.mname_entry.insert(0, '')
            self.bind_validation(self.mname_entry, self.validate_mname)
    
    def mname_entry_leave(self, event):
        if self.mname_entry.get() == '':
            self.mname_entry.delete(0, tk.END)
            self.mname_entry.config(validate="none")
            self.mname_entry.insert(0, 'Middle Initial')
            

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

class ForgotPassword(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.parent = master
        self.master.title('Forgot Password')
        master.minsize(width=851, height=462)
        
        self.config(background='black')
        self.back_image_path = 'back.png'
        self.create_labels()
        self.show_canvas()
        self.show_email_entry()

        master.bind('<Unmap>', self.on_minimize_signup)
        master.bind('<Map>', self.on_restore_signup)
        

    def on_minimize_signup(self, event):
        self.parent.geometry("851x462")

    def on_restore_signup(self, event):
        self.parent.geometry("851x462")

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
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg='#0c0c0c', 
                                highlightbackground='#00FF00', highlightthickness=4)
        self.canvas.grid(row=1, column=4, rowspan=9, columnspan=11, sticky='nsew')
        self.canvas.config(highlightbackground='#00FF00')
        self.canvas.bind('<Button-1>', self.canvas_focus)
        for i in range(11):
            self.grid_rowconfigure(i, weight=1)
        for j in range(19):  
            self.grid_columnconfigure(j, weight=1)

    def show_email_entry(self):
        
        self.pil_image_back_image1 = Image.open(self.back_image_path)
        self.resize_back_image1 = self.pil_image_back_image1.resize((30,30))
        self.image_back_image1 = ImageTk.PhotoImage(self.resize_back_image1)
        self.back_button1 = tk.Label(self, image=self.image_back_image1, bg='#121212', cursor='hand2')
        self.back_button1.place(relx=0.92, rely=0.135, anchor='center')

        self.back_button1.bind('<Button-1>', self.back_btn1)

        self.forgot_pass_lb = tk.Label(self, text="Forgot Password", font=("Montserrat", 40, "bold"),
                                     fg='#00FF00', bg='#0c0c0c', highlightbackground='#00FF00')
        self.forgot_pass_lb.place(relx=0.5, rely=0.2, anchor='center')
        self.entry_email = tk.Entry(self, font=('Monospac821 BT', 17), width=30, justify='center', fg='white', bg='#323232')
        self.entry_email.place(relx=0.5, rely=0.4, anchor='center')
        self.entry_email.insert(0, 'Email')
    
        self.entry_email.bind('<FocusIn>', self.entry_user_enter)
        self.entry_email.bind('<FocusOut>', self.entry_user_leave)

        self.confirm_email_btn = tk.Button(self, text='Search Account', font=('Montserrat', 17, 'bold'), 
                                   fg='#00FF00', bg='#0c0c0c', width=25, cursor='hand2', command=self.send_otp)
        self.confirm_email_btn.place(relx=0.5, rely=0.59, anchor='center')
    
    def canvas_focus(self, event):
        self.focus_set()

    def entry_user_enter(self, event):
        if self.entry_email.get() == 'Email':
            self.entry_email.delete(0, tk.END)
            self.entry_email.insert(0, '')
    
    def entry_user_leave(self, event):
        if self.entry_email.get() == '':
            self.entry_email.delete(0, tk.END)
            self.entry_email.insert(0, 'Email')
    def show_confirm_otp_entry(self, email):
        self.forgot_pass_lb.place_forget()
        self.confirm_email_btn.place_forget()
        self.entry_email.place_forget()
        self.back_button1.place_forget()

        self.pil_image_back_image2 = Image.open(self.back_image_path)
        self.resize_back_image2 = self.pil_image_back_image2.resize((30,30))
        self.image_back_image2 = ImageTk.PhotoImage(self.resize_back_image2)
        self.back_button2 = tk.Label(self, image=self.image_back_image2, bg='#121212', cursor='hand2')
        self.back_button2.place(relx=0.92, rely=0.135, anchor='center')

        self.back_button2.bind('<Button-1>', self.back_btn2)

        self.confirm_otp_lb = tk.Label(self, text="Confirm OTP", font=("Montserrat", 40, "bold"),
                                     fg='#00FF00', bg='#0c0c0c', highlightbackground='#00FF00')
        self.confirm_otp_lb.place(relx=0.5, rely=0.2, anchor='center')

        self.label = tk.Label(self, text="OTP has been sent to your email", font=("Montserrat", 14,),
                                     fg='#00FF00', bg='#0c0c0c', highlightbackground='#00FF00')
        self.label.place(relx=0.5, rely=0.35, anchor='center')

        self.confirm_otp = tk.Entry(self, font=('Monospac821 BT', 14), width=20, justify='center', fg='white', bg='#323232')
        self.confirm_otp.place(relx=0.5, rely=0.45, anchor='center')

        self.bind_validation(self.confirm_otp)

        self.confirm_otp_btn = tk.Button(self, text='Confirm OTP', font=('Montserrat', 17, 'bold'), 
                                   fg='#00FF00', bg='#0c0c0c', width=25, cursor='hand2', command=lambda: self.check_otp(email))
        self.confirm_otp_btn.place(relx=0.5, rely=0.6, anchor='center')
    def validate_input(self, text):
        regex = "^[0-9]*$"
        return re.match(regex, text) is not None
    def bind_validation(self, entry):
        entry.config(validate="key")
        entry.config(validatecommand=(self.register(self.validate_input), "%P"))
    def send_otp(self):
        email = self.entry_email.get()
        
        if self.entry_email.get() == '':
            messagebox.showerror("Error", "Please enter an email")
            return
        
        if self.parent.db_handler.email_search(email):
            self.otp_code = ''
            self.generate_otp(email)
        else:
            messagebox.showerror("Error", "Account does not exists")
            return

    def send_email(self, email):
        emailSender = 'receiver.not404@gmail.com'
        emailPassword = 'yhwb ijon zrxw hpzj'
        emailReceiver = self.entry_email.get()

        subject = 'One-Time-Password'
        body = f"""
        Your One Time Password (OTP) for CHANGE ACCOUNT PASSWORD is: {self.otp_code}. 
        Please use this OTP to complete your change password process. Do not share this OTP with anyone for security reasons
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
        print(self.otp_code)
        self.show_confirm_otp_entry(email)

    def generate_otp(self, email):
        self.otp_code = ''.join(str(randint(0, 9)) for _ in range(6))
        self.send_email(email)

    def check_otp(self, email):
        otp = self.confirm_otp.get().strip()
        if self.otp_code != otp :
            messagebox.showerror("Error", "OTP does not match")
            return
        elif self.confirm_otp.get() == '':
            messagebox.showerror("Error", "Please enter OTP")
            return
        else:
            self.change_function_pass(email)
    def change_function_pass(self, email):
        
        self.confirm_otp_lb.place_forget()
        self.confirm_otp_btn.place_forget()
        self.confirm_otp.place_forget()
        self.label.place_forget()
        self.back_button2.place_forget()

        self.pil_image_back_image3 = Image.open(self.back_image_path)
        self.resize_back_image3 = self.pil_image_back_image3.resize((30,30))
        self.image_back_image3 = ImageTk.PhotoImage(self.resize_back_image3)
        self.back_button3 = tk.Label(self, image=self.image_back_image3, bg='#121212', cursor='hand2')
        self.back_button3.place(relx=0.92, rely=0.135, anchor='center')

        self.back_button3.bind('<Button-1>', self.back_btn3)

        self.change_pass_lb = tk.Label(self, text="Change Password", font=("Montserrat", 35, "bold"),
                                     fg='#00FF00', bg='#0c0c0c', highlightbackground='#00FF00')
        self.change_pass_lb.place(relx=0.5, rely=0.2, anchor='center')

        self.change_lb = tk.Label(self, text="Input new password", font=("Montserrat", 17),
                                     fg='#00FF00', bg='#0c0c0c', highlightbackground='#00FF00')
        self.change_lb.place(relx=0.5, rely=0.32, anchor='center')

        self.new_password = tk.Entry(self, font=('Monospac821 BT', 17), width=30, justify='center', fg='white', bg='#323232', show='')
        self.new_password.place(relx=0.5, rely=0.43, anchor='center')

        self.confirm_new_password1 = tk.Entry(self, font=('Monospac821 BT', 17), width=30, justify='center', fg='white', bg='#323232', show='')
        self.confirm_new_password1.place(relx=0.5, rely=0.53, anchor='center')

        self.change_pass_btn = tk.Button(self, text='Change Password', font=('Montserrat', 17, 'bold'), 
                                   fg='#00FF00', bg='#0c0c0c', width=25, cursor='hand2', command=lambda: self.change_pass(email))
        self.change_pass_btn.place(relx=0.5, rely=0.7, anchor='center')

        self.new_password.insert(0, 'New Password')
        self.confirm_new_password1.insert(0, 'Confirm Password')

        self.new_password.bind('<FocusIn>', self.new_focus)
        self.confirm_new_password1.bind('<FocusIn>', self.confirm_focus)
        self.new_password.bind('<FocusOut>', self.new_focus_out)
        self.confirm_new_password1.bind('<FocusOut>', self.confirm_focus_out)

    def new_focus(self, event):
        if self.new_password.get() == 'New Password':
            self.new_password.delete(0, tk.END)
            self.new_password.insert(0, '')
            self.new_password.config(show='*')

            
    def new_focus_out(self, event):
        if self.new_password.get() == '':
            self.new_password.delete(0, tk.END)
            self.new_password.insert(0, 'New Password')
            self.new_password.config(show='')
            

    def confirm_focus(self, event):
        if self.confirm_new_password1.get() == 'Confirm Password':
            self.confirm_new_password1.delete(0, tk.END)
            self.confirm_new_password1.insert(0, '')
            self.confirm_new_password1.config(show='*')
    
    def confirm_focus_out(self, event):
        if self.confirm_new_password1.get() == '':
            self.confirm_new_password1.delete(0, tk.END)
            self.confirm_new_password1.insert(0, 'Confirm Password')
            self.confirm_new_password1.config(show='')

    def change_pass(self, email):
        password = self.new_password.get().strip()
        email_to_change = email

        if self.new_password.get() == '':
            messagebox.showerror("Error", "Please enter new password")
            return
        elif self.confirm_new_password1.get() == '':
            messagebox.showerror("Error", "Please confirm new password")
            return
        elif self.new_password.get()!= self.confirm_new_password1.get():
            messagebox.showerror("Error", "Passwords do not match")
            return
        else:
            success = self.parent.db_handler.change_pass(email_to_change, password)
            if success:
                messagebox.showinfo("Success", "Password changed successfully")
                self.parent.change_frame('LoginPage')
        
        
    def back_btn3(self, event):
        self.change_pass_lb.place_forget()
        self.change_lb.place_forget()
        self.new_password.place_forget()
        self.confirm_new_password1.place_forget()
        self.change_pass_btn.place_forget()
        self.show_email_entry()

    def back_btn2(self, event):
        self.confirm_otp_lb.place_forget()
        self.confirm_otp_btn.place_forget()
        self.confirm_otp.place_forget()
        self.label.place_forget()
        self.show_email_entry()
        
    def back_btn1(self, event):
        self.parent.change_frame('LoginPage')

class LandingPage(tk.Frame):
    def __init__(self, parent, email = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.configure(bg="black")
        self.is_calculator_on = True

        self.text_strVar = tk.StringVar(value="0")
        self.operator_var = tk.StringVar(value="")
        self.operator = None
        self.first_number = None
        self.reset_next_entry = False
        self.email = email

        self.textBox = tk.Entry(self, textvariable=self.text_strVar, font=("Arial", 50), justify='right', bg="lightgrey")
        self.textBox.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="ew")

        validation = self.register(self.validate_input)
        self.textBox.config(validate="key", validatecommand=(validation, '%P'))
        
        num_lb = [
            "1", "2", "3",
            "4", "5", "6",
            "7", "8", "9",
            "0", "00", ".",
        ]

        for idx, button_data in enumerate(num_lb):
            label_num = tk.Label(self, text=button_data, font=("Arial", 40), bg="black", fg="green", width=4, height=2, cursor='hand2', highlightthickness=2)
            label_num.grid(row=idx // 3 + 3, column=idx % 3, padx=0, pady=0, sticky="nsew")
            label_num.bind("<Button-1>", lambda event, num=button_data: self.update_entry(num))
            label_num.bind("<Enter>", self.change_color_enter)
            label_num.bind("<Leave>", self.change_color_leave)

        operators_lb = ["÷", "×", "−", "+", "="]

        for idx, operators in enumerate(operators_lb):
            label_operators = tk.Label(self, text=operators, font=("Arial", 40), bg="black", fg="green", width=4, height=2, cursor='hand2', highlightthickness=2)
            label_operators.grid(row=idx + 2, column=3, padx=0, pady=0, sticky="nsew")
            if operators == "=": 
                label_operators.bind("<Button-1>", lambda event: self.calculate())
            else:
                label_operators.bind("<Button-1>", lambda event, op=operators: self.update_operators(op))
            label_operators.bind("<Enter>", self.change_color_enter)
            label_operators.bind("<Leave>", self.change_color_leave)
        
        clear_btns = ["On/Off", "C", "AC"]

        for idx, btns in enumerate(clear_btns):
            if btns == "On/Off":
                label_btns = tk.Label(self, text=btns, font=("Arial", 40), background="#50C878", foreground="black", cursor="hand2", highlightthickness=2, width=4, height=2)
            else:
                label_btns = tk.Label(self, text=btns, font=("Arial", 40), bg="black", fg="green", width=4, height=2, cursor='hand2', highlightthickness=2) 
            if idx == 0:  
                label_btns.grid(row=2, column=idx, padx=0, pady=0, sticky="ew", columnspan=idx+1)
            else: 
                label_btns.grid(row=2, column=idx, padx=0, pady=0, sticky="ew")
            if btns == "C":
                label_btns.bind("<Button-1>", lambda event: self.clear_entry())
            elif btns == "AC":
                label_btns.bind("<Button-1>", lambda event: self.all_clear())
            elif btns == "On/Off":
                label_btns.bind("<Button-1>", lambda event: (self.toggle_entry_state(), self.change_color_onOff_click(event)))
            label_btns.bind("<Enter>", self.change_color_enter)
            label_btns.bind("<Leave>", self.change_color_leave)

        for i in range(4):  
            self.columnconfigure(i, weight=1)
        for i in range(13):  
            self.rowconfigure(i, weight=1)
        

        self.bind("<Key>", self.on_key_press)
        self.create_top_section()
        self.focus_set()
        self.textBox.bind("<Key>", self.on_key_press)
        
    def create_top_section(self):
        header_frame = tk.Frame(self, bg='black')
        header_frame.grid(row=0, column=0, columnspan=5, sticky="ew")

        top_label = tk.Label(header_frame, text="Welcome to Dashboard!", font=("Arial", 24), bg="black", fg="green")
        top_label.pack(side="left", expand=True, fill="both")

        profile_button_font = ("Arial", 24)
        button_width = 12 
        profile_button = tk.Button(header_frame, text="View Profile", font=profile_button_font, bg="black", fg="green", command=self.view_profile, width=button_width)
        logout_button = tk.Button(header_frame, text="Log out", font=profile_button_font, bg="black", fg="green", command=self.log_out, width=button_width)

        logout_button.pack(side="right", fill="both",padx=5)
        profile_button.pack(side="right", fill="both", padx=5)
        

        self.textBox.grid(row=1, column=0, columnspan=5, padx=5, pady=5, sticky="ew")

        self.rowconfigure(0, minsize=self.textBox.winfo_reqheight())

    def change_color_onOff_click(self, event):
        current_bg_color = event.widget.cget("bg")
        if current_bg_color == "#50C878":  
            event.widget.config(bg="#C70039", fg="white")
        else:  
            event.widget.config(bg="#50C878", fg="black")

    def change_color_enter(self, event):
        if self.is_calculator_on and event.widget.cget("text") != "On/Off":
            event.widget.config(bg="green", fg="black")

    def change_color_leave(self, event):
        if self.is_calculator_on and event.widget.cget("text") != "On/Off":
            event.widget.config(bg="black", fg="green") 
    
    def toggle_entry_state(self):
        self.focus_set()
        current_state = self.textBox['state']
        if current_state == 'normal':
            self.all_clear()
            self.textBox.config(state='readonly')
            for label in self.grid_slaves():
                if isinstance(label, tk.Label) and label.cget("text") != "On/Off":
                    label.unbind("<Button-1>")
            self.is_calculator_on = False 
        else:
            self.textBox.config(state='normal')
            for label in self.grid_slaves():
                if isinstance(label, tk.Label) and label.cget("text") != "On/Off":
                    label.bind("<Button-1>", self.label_click_event)
            self.is_calculator_on = True

    def label_click_event(self, event):
        label_text = event.widget.cget("text")
        if label_text.isdigit() or label_text in [".", "00"]:
            self.update_entry(label_text)
        
    def clear_entry(self):
        self.text_strVar.set('0')

    def all_clear(self):
        self.text_strVar.set('0')
        self.operator = None
        self.first_number = None
        self.reset_next_entry = False

    def validate_input(self, new_text):
        if new_text == "" or new_text == "Error":
            return True
        try:
            float(new_text) 
            return True
        except ValueError:
            return False
    
    def update_entry(self, value):
        if self.text_strVar.get() == "Error":
            return
        if self.reset_next_entry:
            self.text_strVar.set('')
            self.reset_next_entry = False

        cursor_position = self.textBox.index(tk.INSERT)
        current_text = self.text_strVar.get()

        if current_text == "0" and value not in ["00", "."]:
            new_text = value
        else:
            if value == '00' and not current_text.startswith('0'):
                if cursor_position == 0 or (current_text[cursor_position - 1] in '0123456789'):
                    pass
                else:
                    return

            if value == '.' and '.' in current_text.split()[-1]:
                return

            new_text = current_text[:cursor_position] + value + current_text[cursor_position:]

        if self.validate_input(new_text):
            self.text_strVar.set(new_text)
            self.textBox.icursor(cursor_position + len(value))

    def update_operators(self, operator):
        operator_conversion = {"÷": "/", "×": "*", "−": "-", "+": "+"}
        if operator in operator_conversion:
            operator = operator_conversion[operator]

        if self.text_strVar.get() and (self.first_number is None or self.reset_next_entry):
            self.first_number = self.text_strVar.get()
            self.operator = operator
            self.reset_next_entry = True
            self.text_strVar.set('')

    def calculate(self):
        if not self.operator or self.reset_next_entry:
            return
        second_number = self.text_strVar.get().lstrip("0") or "0"  
        first_number = self.first_number.lstrip("0") or "0"

        try:
            expression = f"{first_number}{self.operator}{second_number}"
            result = eval(expression)
            self.text_strVar.set(str(result))
        except Exception as e:
            self.text_strVar.set("Error")
        finally:
            self.first_number = None
            self.operator = None
            self.reset_next_entry = False

    def on_key_press(self, event):
        char = event.char
        keysym = event.keysym
        
        if char in '0123456789':
            self.update_entry(char)
        elif char in '+-*/':
            self.update_operators(char)
        elif keysym == 'Return':
            self.calculate()
        elif keysym == 'Escape':
            self.all_clear()
        elif keysym == 'BackSpace':
            self.clear_entry()
        elif char == '.':
            self.update_entry(char)

    def view_profile(self):
        self.master.change_frame('ViewPage', email=self.email)

    def log_out(self):
        confirm_logout = tk.messagebox.askyesno("Confirm Log Out", "Are you sure you want to log out?")
        if confirm_logout:
            self.master.change_frame('LoginPage')

class ViewPage(tk.Frame):
    def __init__(self, master, email = None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        self.parent = master
        self.email = email
        self.master.title('View Profile')
        self.config(background='black')
        self.back_image_path = 'back.png'
        master.minsize(width=850, height=592)
        master.bind('<Unmap>', self.on_minimize)
        master.bind('<Map>', self.on_restore)
        self.create_labels()
        self.show_canvas()
        self.get_info()
    def get_info(self):
        self.update()
        
        self.name.delete(0, tk.END)
        self.name.insert(0, f"{self.user_info[0].fname} {self.user_info[0].mname} {self.user_info[0].lname}")

        self.location.delete(0, tk.END)
        self.location.insert(0, f"{self.user_info[0].city}, {self.user_info[0].province}")

        self.gender.delete(0, tk.END)
        self.gender.insert(0, f"{self.user_info[0].gender}")

        self.status.delete(0, tk.END)
        self.status.insert(0, f"{self.user_info[0].status}")

        image_data = self.user_info[0].image_data
        image = Image.open(io.BytesIO(image_data))
        image = image.resize((200, 200), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.profile.config(image=photo)
        self.profile.image = photo

        self.name.config(state='readonly', fg='#00FF00', readonlybackground="#0c0c0c")
        self.location.config(state='readonly', fg='#00FF00', readonlybackground="#0c0c0c")
        self.gender.config(state='readonly', fg='#00FF00', readonlybackground="#0c0c0c")
        self.status.config(state='readonly', fg='#00FF00', readonlybackground="#0c0c0c")
        
    def update(self):
        key = self.email
        db_conn = db_handler.DBHandler()
        self.user_info = db_conn.view_account(key)
        db_conn.close()

    def on_minimize(self, event):
        self.parent.geometry("850x592")

    def on_restore(self, event):
        self.parent.geometry("850x592")
        
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
        
        self.profile = tk.Label(self, text='No Image Uploaded', font=('Monospac821 BT', 12), fg='#00FF00', bg='#0c0c0c', image='')
        self.profile.place(relx=0.44, rely=0.3, anchor='w')

        def center_label(event=None):
            window_width = self.winfo_width()
            label_width = self.profile.winfo_reqwidth()
            label_x = (window_width - label_width) / 2
            self.profile.place(relx=label_x / window_width, rely=0.3, anchor='w')

        center_label()

        self.bind("<Configure>", center_label)
        
        self.pil_image_back_image = Image.open(self.back_image_path)
        self.resize_back_image = self.pil_image_back_image.resize((30,30))
        self.image_back_image = ImageTk.PhotoImage(self.resize_back_image)
        self.back_button = tk.Label(self, image=self.image_back_image, bg='#121212', cursor='hand2')
        self.back_button.place(relx=0.92, rely=0.135, anchor='center')

        self.back_button.bind('<Button-1>', self.back_btn)


        self.name = tk.Entry(self, font=('Monospac821 BT', 17), width=30, justify='center', fg='white', bg='#0c0c0c', highlightthickness=0)
        self.name.place(relx=0.5, rely=0.5, anchor='center')
        self.name.insert(0, "Name")

        self.location = tk.Entry(self, font=('Monospac821 BT', 17), width=30, justify='center', fg='white', bg='#0c0c0c', highlightthickness=0)
        self.location.place(relx=0.5, rely=0.6, anchor='center')
        self.location.insert(0, "Location")

        self.gender = tk.Entry(self, font=('Monospac821 BT', 17), width=30, justify='center', fg='white', bg='#0c0c0c', highlightthickness=0)
        self.gender.place(relx=0.5, rely=0.7, anchor='center')
        self.gender.insert(0, "Gender")

        self.status = tk.Entry(self, font=('Monospac821 BT', 17), width=30, justify='center', fg='white', bg='#0c0c0c', highlightthickness=0)
        self.status.place(relx=0.5, rely=0.8, anchor='center')
        self.status.insert(0, "Status")

        self.edit = tk.Label(self, text="Edit", font=('Monospac821 BT', 11, 'underline'), fg='#FFFFFF', bg='#0c0c0c', cursor='hand2')
        self.edit.place(relx=0.49, rely=0.87, anchor='w')

        self.edit.bind('<Button-1>', self.edit_profile)

    def back_btn(self, event):
        email = self.email
        self.parent.change_frame('LandingPage', email=email)
    def edit_profile(self, event):
        email = self.email
        self.parent.change_frame('EditProfile', email=self.email)

    def format_text(self, text, max_chars):
        if len(text) <= max_chars:
            return text
        else:
            parts = [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
            return '\n'.join(parts)

class EditProfile(tk.Frame):
    def __init__(self, master, email = None):
        tk.Frame.__init__(self, master)
        self.parent = master
        self.master.title('Edit Profile')
        self.email = email
        master.minsize(width=1062, height=638)
        master.bind('<Unmap>', self.on_minimize_edit)
        master.bind('<Map>', self.on_restore_edit)
        self.config(background='black')
        self.create_labels()
        self.show_canvas()
        
    def on_minimize_edit(self, event):
        self.parent.geometry("1062x638")

    def on_restore_edit(self, event):
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
        self.canvas.grid(row=1, column=3, rowspan=9, columnspan=13, sticky='nsew')
        for i in range(11):
            self.grid_rowconfigure(i, weight=1)
        for j in range(19):  
            self.grid_columnconfigure(j, weight=1)
        self.show_object()

    def show_object(self):
        self.update()
        self.label = tk.Label(self.canvas, text='Edit Profile', font=('Montserrat', 25, 'bold'), fg='#00FF00', bg='#0c0c0c')
        self.label.place(relx=0.5, rely=0.02, anchor='n')

        self.personal_label = tk.Label(self, text='Personal Info', font=('Monospac821 BT', 11), fg='#00FF00', bg='#0c0c0c')
        self.personal_label.place(relx=0.2, rely=0.21, anchor='w')

        self.fname_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=20, justify='center', fg='white', bg='#323232')
        self.fname_entry.place(relx=0.3, rely=0.28, anchor='center')
        
        self.mname_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=20, justify='center', fg='white', bg='#323232')
        self.mname_entry.place(relx=0.3, rely=0.36, anchor='center')

        self.lname_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=20, justify='center', fg='white', bg='#323232')
        self.lname_entry.place(relx=0.3, rely=0.44, anchor='center')

        self.other_label = tk.Label(self, text='Other Info', font=('Monospac821 BT', 11), fg='#00FF00', bg='#0c0c0c')
        self.other_label.place(relx=0.2, rely=0.54, anchor='w')

        self.gender_options = ["Gender","Male", "Female", "Others"]
        self.gender_var = tk.StringVar()
        self.gender_var.set(self.user_info[0].gender)

        self.gender = tk.OptionMenu(self, self.gender_var, *self.gender_options)
        self.gender.config(bg='#0c0c0c', fg='#00FF00', font=('Monospac821 BT', 12), width=15, highlightbackground='#0c0c0c', highlightthickness=1)
        self.gender.place(relx=0.225, rely=0.6, anchor='w')

        self.city_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=20, justify='center', fg='white', bg='#323232')
        self.city_entry.place(relx=0.3, rely=0.68, anchor='center')

        self.province_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=20, justify='center', fg='white', bg='#323232')
        self.province_entry.place(relx=0.3, rely=0.77, anchor='center')

        self.marital_status_options = [
            "Status",
            "Single",
            "Married",
            "Widowed",
            "Divorced",
            "Separated",
            "Annulled",
            "In a Relationship",
            "Other"]
        self.marital_status_var = tk.StringVar()
        self.marital_status_var.set(self.user_info[0].status)
        self.marital_status_menu = tk.OptionMenu(self, self.marital_status_var, *self.marital_status_options)
        self.marital_status_menu.config(bg='#0c0c0c', fg='#00FF00', font=('Monospac821 BT', 12), width=17, highlightbackground='#0c0c0c', highlightthickness=1)
        self.marital_status_menu.place(relx=0.225, rely=0.85, anchor='w')

        self.back_image_path = 'back.png'
        self.pil_image_back_image = Image.open(self.back_image_path)
        self.resize_back_image = self.pil_image_back_image.resize((30,30))
        self.image_back_image = ImageTk.PhotoImage(self.resize_back_image)
        self.back_button = tk.Label(self, image=self.image_back_image, bg='#0c0c0c', cursor='hand2')
        self.back_button.place(relx=0.75, rely=0.15, anchor='center')

        self.image_label = tk.Label(self, text='No Image Uploaded', font=('Monospac821 BT', 12), fg='#00FF00', bg='#0c0c0c', cursor='hand2', image='')
        self.image_label.place(relx=0.6, rely=0.4, anchor='w')

        image_data = self.user_info[0].image_data
        image = Image.open(io.BytesIO(image_data))
        self.original_image = image
        image = image.resize((200, 200), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo)
        self.image_label.image = photo

        self.change_profile_btn = tk.Button(self, text='Change Profile', font=('Montserrat', 14, 'bold'), 
                                   fg='#00FF00', bg='#0c0c0c', width=15, cursor='hand2', command=self.upload_image)
        self.change_profile_btn.place(relx=0.6, rely=0.6, anchor='w')

        self.crop_btn = tk.Button(self, text='Crop', font=('Montserrat', 14, 'bold'), 
                                   fg='#00FF00', bg='#0c0c0c', width=15, cursor='hand2', command=self.start_crop)
        self.crop_btn.place(relx=0.6, rely=0.7, anchor='w')

        self.filter_options = ["Select Filter","Original", "Grayscale", "Blur", "Sharpen",
                              "Contour", "Edge Enhance", "Emboss", "Smooth", "Brightness", "Contrast"]
        self.filter_var = tk.StringVar()
        self.filter_var.set(self.filter_options[0])

        self.filter_menu = tk.OptionMenu(self, self.filter_var, *self.filter_options, command=self.apply_filter)
        self.filter_menu.config(bg='#0c0c0c', fg='#00FF00', font=('Monospac821 BT', 14), width=15, highlightbackground='#0c0c0c', highlightthickness=1)
        self.filter_menu.place(relx=0.6, rely=0.8, anchor='w')

        self.save_btn = tk.Button(self, text='Save', font=('Montserrat', 12, 'bold'), 
                                   fg='#00FF00', bg='#0c0c0c', width=15, cursor='hand2', command=self.onclick_create)
        self.save_btn.place(relx=0.43, rely=0.8, anchor='w')


        self.fname_entry.insert(0, f"{self.user_info[0].fname}")
        self.mname_entry.insert(0, f"{self.user_info[0].mname}")
        self.lname_entry.insert(0, f"{self.user_info[0].lname}")
        self.city_entry.insert(0, f"{self.user_info[0].city}")
        self.province_entry.insert(0, f"{self.user_info[0].province}")

        self.bind_validation(self.fname_entry)
        self.bind_validation(self.lname_entry)
        self.bind_validation(self.city_entry)
        self.bind_validation(self.province_entry)

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
        self.filter_menu.place(relx=0.6, rely=0.8, anchor='w')
        self.crop_btn.place(relx=0.6, rely=0.7, anchor='w')
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            self.original_image = Image.open(file_path)
            self.original_image = self.original_image.resize((200, 200), Image.LANCZOS)
            self.filtered_image = self.original_image.copy()
            self.photo = ImageTk.PhotoImage(self.original_image)
            self.image_label.config(image=self.photo)
            self.image_label.image = self.photo
        else:
            return 

    def start_crop(self):
        if self.original_image is None:
            messagebox.showerror("Error", "Please load an image first.")
            return

        self.top = tk.Toplevel(self)
        self.top.title("Crop Image")
        photo = ImageTk.PhotoImage(self.original_image)
        self.top.resizable(False, False)
        if hasattr(self, 'original_image'):
            self.crop_canvas = tk.Canvas(self.top, width=self.original_image.width, height=self.original_image.height)
            self.crop_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        elif hasattr(self, 'filtered_image'):
            self.crop_canvas = tk.Canvas(self.top, width=self.filtered_image.width, height=self.filtered_image.height)
            self.crop_canvas.create_image(0, 0, anchor=tk.NW, image=photo)

        self.crop_canvas.pack()
        self.crop_canvas.bind("<Button-1>", self.on_crop_start)
        self.crop_canvas.bind("<B1-Motion>", self.on_crop_drag)
        self.crop_canvas.bind("<ButtonRelease-1>", self.on_crop_end)

        self.crop_rect = None
        self.crop_start = None
        self.image = photo

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

    def bind(self):
        self.fname_entry.bind('<FocusIn>', self.fname_entry_enter)
        self.fname_entry.bind('<FocusOut>', self.fname_entry_leave)
        self.lname_entry.bind('<FocusIn>', self.lname_entry_enter)
        self.lname_entry.bind('<FocusOut>', self.lname_entry_leave)
        self.mname_entry.bind('<FocusIn>', self.mname_entry_enter)
        self.mname_entry.bind('<FocusOut>', self.mname_entry_leave)
        self.city_entry.bind('<FocusIn>', self.city_entry_enter)
        self.city_entry.bind('<FocusOut>', self.city_entry_leave)
        self.province_entry.bind('<FocusIn>', self.province_entry_enter)
        self.province_entry.bind('<FocusOut>', self.province_entry_leave)
        self.back_button.bind('<Button-1>', self.onclick_back)
        self.canvas.bind('<Button-1>', self.canvas_clicked)
    def update(self):
        key = self.email
        db_conn = db_handler.DBHandler()
        self.user_info = db_conn.view_account(key)
        db_conn.close()

    def validate_input(self, text):
        regex = "^[A-Za-z ]*$"
        if re.match(regex, text):
            return True
        else:
            return False
    def validate_mname(self, text):
        return len(text) <= 1 and self.validate_input(text)
    
    def bind_validation(self, entry, validate_func=None):
        entry.config(validate="key")
        if validate_func:
            entry.config(validatecommand=(self.register(validate_func), "%P"))
        else:
            entry.config(validatecommand=(self.register(self.validate_input), "%P"))


    def onclick_create(self):
        fname = self.fname_entry.get()
        mname = self.mname_entry.get()
        lname = self.lname_entry.get()
        gender = self.gender_var.get()
        city = self.city_entry.get()
        province = self.province_entry.get()
        status = self.marital_status_var.get()
        email = self.email
        
        if not self.validate_input(fname):
            messagebox.showerror('Error', 'First Name must contain only letters')
            return
        elif not self.validate_input(mname):
            if mname == 'MI (Optional)':
                mname = 'N/A'
            elif not mname.strip():
                mname = 'N/A'
            else:
                messagebox.showerror('Error', 'Middle Initial must contain only letters')
                return
        elif not self.validate_input(lname):
            messagebox.showerror('Error', 'Last Name must contain only letters')
            return
        
        if self.gender_var.get() == "Gender":
            messagebox.showerror('Error', 'Please select gender')
            return
        
        if self.marital_status_var.get() == "Status":
            messagebox.showerror('Error', 'Please select marital status')
            return

        if not city.replace(" ", "").isalpha():
            messagebox.showerror('Error', 'City must contain only letters')
            return
        
        if not province.replace(" ", "").isalpha():
            messagebox.showerror('Error', 'Province must contain only letters')
            return

        if mname == f"{self.user_info[0].mname}":
            mname = f"{self.user_info[0].mname}"
        elif not mname.strip():
            mname = ""
        elif mname.isalpha():
            pass
        else:
            messagebox.showerror('Error', 'Middle Initial must contain only letters')
            return
        image_data = None

        profile = models.Profiles()
        profile.fname = fname
        profile.mname = mname
        profile.lname = lname
        profile.gender = gender
        profile.city = city
        profile.province = province
        profile.status = status

        if hasattr(self, 'cropped_image'):
            image_to_save = self.cropped_image
        elif hasattr(self, 'filtered_image'):
            image_to_save = self.filtered_image
        elif hasattr(self, 'original_image'):
            image_to_save = self.original_image

        if 'image_to_save' in locals():
            with io.BytesIO() as buffer:
                image_to_save.save(buffer, format='PNG')
                image_data = buffer.getvalue()

        db_conn = db_handler.DBHandler()            
        db_conn.edit_info_db(email, fname, mname, lname, gender, city, province, status, image_data)
        db_conn.close()

        messagebox.showinfo('Successfully Updated', f'Information updated for {profile.fname}')
        self.parent.change_frame('LandingPage', email=email)

    def onclick_back(self, event):
        fname = self.fname_entry.get()
        mname = self.mname_entry.get()
        lname = self.lname_entry.get()
        gender = self.gender_var.get()
        city = self.city_entry.get()
        province = self.province_entry.get()
        status = self.marital_status_var.get()
        email = self.email
        if  fname == f'{self.user_info[0].fname}' and mname == f'{self.user_info[0].mname}' and lname == f'{self.user_info[0].lname}' and gender == f'{self.user_info[0].gender}' and city == f'{self.user_info[0].city}' and province == f'{self.user_info[0].province}' and status == f'{self.user_info[0].status}':
            self.parent.change_frame('ViewPage', email=email)
        elif fname or mname or lname or gender or city or province or status:
            confirmed = messagebox.askyesno('Warning', 'Are you sure you want to cancel?')
            if not confirmed:
                return
            else:
                self.parent.change_frame('ViewPage', email=email)
        else:
            return
        self.back_button.config(bg='#323232')

    def city_entry_enter(self, event):
        if self.city_entry.get() == f'{self.user_info[0].city}':
            self.city_entry.delete(0, tk.END)
            self.city_entry.insert(0, '')
    
    def city_entry_leave(self, event):
        if self.city_entry.get() == '':
            self.city_entry.delete(0, tk.END)
            self.city_entry.insert(0, f'{self.user_info[0].city}')

    def province_entry_enter(self, event):
        if self.province_entry.get() == f'{self.user_info[0].province}':
            self.province_entry.delete(0, tk.END)
            self.province_entry.insert(0, '')

    def province_entry_leave(self, event):
        if self.province_entry.get() == '':
            self.province_entry.delete(0, tk.END)
            self.province_entry.insert(0, f'{self.user_info[0].province}')

    def mname_entry_enter(self, event):
        if self.mname_entry.get() == f'{self.user_info[0].mname}':
            self.mname_entry.delete(0, tk.END)
            self.mname_entry.config(validate="key")
            self.mname_entry.insert(0, '')
            self.bind_validation(self.mname_entry, self.validate_mname)
    def mname_entry_leave(self, event):
        if self.mname_entry.get() == '':
            self.mname_entry.delete(0, tk.END)
            # self.mname_entry.config(validate="none")
            # self.mname_entry.insert(0, f'{self.user_info[0].mname}')

    def lname_entry_leave(self, event):
        if self.lname_entry.get() == '':
            self.lname_entry.delete(0, tk.END)
            self.lname_entry.insert(0, f'{self.user_info[0].lname}')

    def lname_entry_enter(self, event):
        if self.lname_entry.get() == f'{self.user_info[0].lname}':
            self.lname_entry.delete(0, tk.END)
            self.lname_entry.insert(0, '')

    def fname_entry_enter(self, event):
        if self.fname_entry.get() == f'{self.user_info[0].fname}':
            self.fname_entry.delete(0, tk.END)
            self.fname_entry.insert(0, '')
            

    def fname_entry_leave(self, event):
        if self.fname_entry.get() == '' :
            self.fname_entry.delete(0, tk.END)
            self.fname_entry.insert(0, f'{self.user_info[0].fname}')

    def canvas_clicked(self, event):
        self.focus_set()

    def onclick(self, event):
        email = self.email
        self.parent.change_frame('ViewPage', email=email)