import tkinter as tk
from tkinter import ttk

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
    def __init__(self):
        super().__init__()

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
        self.canvas.grid(row=1, column=4, rowspan=7, columnspan=8, sticky='nsew')
        self.canvas.bind('<Button-1>', self.canvas_clicked)
        self.show_object()

    def show_object(self):
        
        self.sign_in_lb = tk.Label(self, text="SIGN IN", font=("Montserrat", 30, "bold"),
                                     fg='#00FF00', bg='#0c0c0c')
        self.canvas.create_window(self.canvas_width // 1.75 , self.canvas_height // 6, window=self.sign_in_lb)

        self.entry_email = tk.Entry(self, font=('Montserrat', 17), width=30, justify='center', fg='white', bg='#323232')
        self.canvas.create_window(self.canvas_width // 1.75 , self.canvas_height // 3, window=self.entry_email)

        self.entry_email.insert(0, 'Email')
        self.entry_email.bind('<FocusIn>', self.entry_user_enter)
        self.entry_email.bind('<FocusOut>', self.entry_user_leave)

        self.entry_pass = tk.Entry(self, font=('Montserrat', 17), width=30, justify='center', fg='white', bg='#323232')
        self.canvas.create_window(self.canvas_width // 1.75 , self.canvas_height // 2, window=self.entry_pass)

        self.entry_pass.insert(0, 'Password')
        self.entry_pass.bind('<FocusIn>', self.entry_pass_enter)
        self.entry_pass.bind('<FocusOut>', self.entry_pass_leave)

        self.login_btn = tk.Button(self, text='LOGIN', font=('Montserrat', 13, 'bold'), 
                                   fg='#00FF00', bg='#0c0c0c', width=10)
        self.canvas.create_window(self.canvas_width // 1.75 , self.canvas_height // 1.5, window=self.login_btn)

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


