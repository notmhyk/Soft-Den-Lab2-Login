import tkinter as tk
import pages
import db_handler

class MainWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title('Login/Logout')
        self.db_handler = db_handler.DBHandler()
        self.frames = dict()
        self.frames['LoginPage'] = pages.LoginPage(self)
        self.frames['SignUpPage'] = pages.SignUpPage(self)
        self.frames['LandingPage'] = pages.LandingPage(self)
        self.change_frame('LoginPage')

    def change_frame(self, name):
        for frame in self.frames.values():
            frame.grid_forget()
        if name == 'LoginPage':
            self.frames[name] = pages.LoginPage(self)
        elif name == 'SignUpPage':
            self.frames[name] = pages.SignUpPage(self)
        elif name == 'LandingPage':
            self.frames[name] = pages.LandingPage(self)
        self.frames[name].grid(row=0, column=0, sticky='nsew')
        

root = MainWindow()
root.state('zoomed')
root.grid_rowconfigure(0, weight=1)  
root.grid_columnconfigure(0, weight=1)
root.mainloop()