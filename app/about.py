import tkinter as tk
from tkinter import ttk
import webbrowser

def callback(event):
    webbrowser.open_new(event.widget.cget("text"))

class AboutWindow():
    def __init__(self, parent):
        # Create a variable with which we can reference our parent
        self.parent = parent
        # Secondary windows are made using tk.Toplevel() instead of using parent
        self.window = tk.Toplevel()
        self.window.geometry("500x300")
        self.window.title("Login")
        # Labels
        self.labels = [
            tk.Label(self.window, text="pbTools Image Editor", font=('Arial', 20)), 
            tk.Label(self.window, text="For when you just want to do some quick and simple editing\nwithout wanting to bother with Photoshop.", font=('Arial', 14), justify=tk.LEFT), 
            tk.Label(self.window, text="Copyright (C) Paul Baumgarten", font=('Arial', 14)), 
            tk.Label(self.window, text="https://imageeditor.pbtools.app/", font=('Arial', 14), fg="blue", cursor="hand"), 
            tk.Label(self.window, text="---", font=('Arial', 20)), 
            tk.Label(self.window, text="Icons by https://icons8.com", font=('Arial', 10))
            ]
        y = 10
        for label in self.labels:
            label.place(x=20, y=y)
            y+=40
        # Set the hyperlink 
        self.labels[2].bind("<Button-1>", callback) # From https://stackoverflow.com/a/32985240/10971929
        # Button
        self.close_button = tk.Button(self.window, text="Close", command=self.close)
        self.close_button.place(x=20,y=y)
        self.history = []
     
    def close(self):
        self.window.destroy()
