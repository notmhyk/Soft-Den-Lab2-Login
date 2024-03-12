import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

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

        self.entry_email = tk.Entry(self, font=('Montserrat', 17), width=30, justify='center', fg='white', bg='#323232')
        self.canvas.create_window(self.canvas_width // 1.75 , self.canvas_height // 3, window=self.entry_email)

        self.entry_email.insert(0, 'Email')
        

        self.entry_pass = tk.Entry(self, font=('Montserrat', 17), width=30, justify='center', fg='white', bg='#323232')
        self.canvas.create_window(self.canvas_width // 1.75 , self.canvas_height // 2, window=self.entry_pass)

        self.entry_pass.insert(0, 'Password')
        

        self.login_btn = tk.Button(self, text='LOGIN', font=('Montserrat', 17, 'bold'), 
                                   fg='#00FF00', bg='#0c0c0c', width=25, cursor='hand2')
        self.canvas.create_window(self.canvas_width // 1.75 , self.canvas_height // 1.3, window=self.login_btn)

        self.forgot_pass_label = tk.Label(self, text='Forgot Password', font=('Montserrat', 11, 'underline'), 
                                          bg='#0c0c0c', fg='white', cursor='hand2')
        self.canvas.create_window(self.canvas_width // 3.4 , self.canvas_height // 1.6, window=self.forgot_pass_label)

        self.signup_label = tk.Label(self, text='SIGN-UP', font=('Montserrat', 11, 'bold'), bg='#0c0c0c', fg='#00FF00', cursor='hand2')
        self.canvas.create_window(self.canvas_width // 1.11 , self.canvas_height // 1.6, window=self.signup_label)

        self.bind()

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
        self.canvas.grid(row=1, column=3, rowspan=7, columnspan=10, sticky='nsew')
        self.show_object()
        
    def show_object(self):

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
        self.canvas.create_window(self.canvas_width // 1.4, self.canvas_height // 4, window=self.account_label)

        self.email_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=30, justify='center', fg='white', bg='#323232')
        self.canvas.create_window(self.canvas_width // 1, self.canvas_height // 2.7, window=self.email_entry)

        self.pass_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=30, justify='center', fg='white', bg='#323232')
        self.canvas.create_window(self.canvas_width // 1, self.canvas_height // 2, window=self.pass_entry)

        self.confirm_pass_entry = tk.Entry(self, font=('Monospac821 BT', 12), width=30, justify='center', fg='white', bg='#323232')
        self.canvas.create_window(self.canvas_width // 1, self.canvas_height // 1.57, window=self.confirm_pass_entry)

        self.image_pil3 = Image.open(self.image_path)
        self.resize_image3 = self.image_pil3.resize((420,370))
        self.image3 = ImageTk.PhotoImage(self.resize_image3)
        self.canvas.create_image(self.canvas_width // 1, self.canvas_height // 1.7, image=self.image3)

        self.create_btn = tk.Button(self, text='Create Account', font=('Montserrat', 14, 'bold'), 
                                   fg='#00FF00', bg='#0c0c0c', width=15, cursor='hand2')
        self.canvas.create_window(self.canvas_width // 1 , self.canvas_height // 1.3, window=self.create_btn)

        self.back_image_path = 'back.png'
        self.pil_image_back_image = Image.open(self.back_image_path)
        self.resize_back_image = self.pil_image_back_image.resize((30,30))
        self.image_back_image = ImageTk.PhotoImage(self.resize_back_image)
        self.back_button = tk.Label(self, image=self.image_back_image, bg='#0c0c0c')
        self.canvas.create_window(self.canvas_width // 0.74, self.canvas_height // 10, window=self.back_button)


        self.fname_entry.insert(0, 'First Name')
        self.mname_entry.insert(0, 'Middle Name')
        self.lname_entry.insert(0, 'Last Name')
        self.email_entry.insert(0, 'Email')
        self.pass_entry.insert(0, 'Password')
        self.confirm_pass_entry.insert(0, 'Confirm Password')
        self.contact_entry.insert(0, 'Contact Number')
        self.city_entry.insert(0, 'City')
        self.province_entry.insert(0, 'Province')

        self.bind()

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
        self.back_button.config(bg='#323232')
        self.parent.change_frame('LoginPage')

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
            self.contact_entry.insert(0, '')
            
    def contact_entry_leave(self, event):
        if self.contact_entry.get() == '':
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
        if self.mname_entry.get() == 'Middle Name':
            self.mname_entry.delete(0, tk.END)
            self.mname_entry.insert(0, '')
    
    def mname_entry_leave(self, event):
        if self.mname_entry.get() == '':
            self.mname_entry.delete(0, tk.END)
            self.mname_entry.insert(0, 'Middle Name')

    def mname_entry_enter(self, event):
        if self.mname_entry.get() == 'Middle Name':
            self.mname_entry.delete(0, tk.END)
            self.mname_entry.insert(0, '')
    
    def mname_entry_leave(self, event):
        if self.mname_entry.get() == '':
            self.mname_entry.delete(0, tk.END)
            self.mname_entry.insert(0, 'Middle Name')

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
