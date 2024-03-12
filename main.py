import tkinter as tk
import pages

class MainWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title('Login/Logout')
        self.frames = dict()
        self.frames['LoginPage'] = pages.LoginPage(self)
        self.frames['SignUpPage'] = pages.SignUpPage(self)
        self.change_frame('LoginPage')

    def change_frame(self, name):
        for frame in self.frames.values():
            frame.grid_forget()
        if name == 'LoginPage':
            self.frames[name] = pages.LoginPage(self)
        elif name == 'SignUpPage':
            self.frames[name] = pages.SignUpPage(self)
        self.frames[name].grid(row=0, column=0)
        

root = MainWindow()
root.state('zoomed')
root.mainloop()