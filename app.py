import tkinter as tk
from tkinter import ttk

ALLOWED_FILES = (("JPEG files","*.jpg"),("PNG files","*.png"),("all files","*.*"))

class AboutWindow():
    def __init__(self, parent):
        # Create a variable with which we can reference our parent
        self.parent = parent
        # Secondary windows are made using tk.Toplevel() instead of using parent
        self.window = tk.Toplevel()
        self.window.geometry("400x300")
        self.window.title("Login")
        # Labels
        text = ["pbTools Image Editor", "Copyright (C) 2020", "Paul Baumgarten", "https://imageeditor.pbtools.app/"]
        self.labels = []
        y = 40
        for line in text:
            self.labels.append( tk.Label(self.window, text=line ))
            self.labels[ len(self.labels) -1 ].place(x=20, y=y)
            y+=40
        # Button
        self.close_button = tk.Button(self.window, text="Close", command=self.close)
        self.close_button.place(x=20,y=y)
        self.history = []
     
    def close(self):
        self.window.destroy()

class AppWindow():
    def __init__(self, parent):
        # Create the window
        self.parent = parent                # Save a reference to our parent object
        self.window = tk.Toplevel()         # Create a window
        self.window.geometry("800x660")     # Set pixel dimensions 400 wide by 200 high
        self.window.title("PBtools image editor")       # Set window title text
        self.window.state('zoomed')         # Maximise window
        self.window.protocol("WM_DELETE_WINDOW", self.window.quit) # Enable the close icon
        dimensions = (self.window.winfo_height(), self.window.winfo_width())
        # Add all your widgets here...
        self.image_frame = tk.Frame(self.window)
        self.toolbar_frame = tk.Frame(self.window)
        self.bottombar_frame = tk.Frame(self.window)

        self.generate_menu()
        self.generate_toolbar()
    
    def generate_toolbar(self, target):
        self.toolbar_buttons = [
            tk.Button(target, text="Resize", command=self.resize),
            tk.Button(target, text="Crop", command=self.crop),
            tk.Button(target, text="Text", command=self.text),
            tk.Button(target, text="Pen", command=self.pen),
            tk.Button(target, text="Line", command=self.line),
            tk.Button(target, text="Rectangle", command=self.rectangle),
            tk.Button(target, text="Elipse", command=self.elipse),
            tk.Button(target, text="Erase", command=self.erase),
            tk.Button(target, text="Foreground", command=self.setforeground),
            tk.Button(target, text="Background", command=self.setbackground),
        ]
#        for button in toolbar_buttons:

    
    def resize(self):
        pass

    def crop(self):
        pass
    
    def text(self):
        pass

    def pen(self):
        pass

    def line(self):
        pass

    def rectangle(self):
        pass

    def elipse(self):
        pass

    def erase(self):
        pass

    def setforeground(self):
        pass

    def setbackground(self):
        pass

    def undo(self):
        pass

    def add_to_history(self):
        pass

    def revert(self):
        while len(self.history) > 0:
            self.undo()
    
    def generate_menu(self):
        # Create a menu bar
        menubar = tk.Menu(self.window)
        # Create a sub menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.file_open)
        filemenu.add_command(label="Save", command=self.file_saveas)
        filemenu.add_command(label="Save as", command=self.file_saveas)
        filemenu.add_command(label="Set default folder", command=self.folder_set_default)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.window.quit)
        # Create a sub menu
        editmenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Undo", command=self.undo)
        filemenu.add_command(label="Revert", command=self.revert)
        #filemenu.add_command(label="Copy", command=self.file_open)
        #filemenu.add_command(label="Paste", command=self.file_open)
        # Create a sub menu
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.about)
        # Link the sub menus to the menu bar
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Edit", menu=editmenu)
        menubar.add_cascade(label="Help", menu=helpmenu)
        # Set menu to the window
        self.window.config(menu=menubar)
    
    def file_open(self):
        filename = filedialog.askopenfilename(initialdir=self.default_folder, title="Select file", filetypes=ALLOWED_FILES)

    def file_save(self):
        pass

    def file_saveas(self):
        filename = filedialog.asksaveasfilename(initialdir=self.default_folder, title="Select file", filetypes=ALLOWED_FILES)

    def folder_set_default(self):
        self.default_folder = filedialog.askdirectory(initialdir=self.default_folder, title = "Select folder containing student photos")

    def about(self):
        about = AboutWindow(self.window)

if __name__ == "__main__":
    root = tk.Tk()          # Initialise the tk system into an object called `root`
    root.withdraw()         # Hide the default window
    app = AppWindow(root)   # Run our window, called AppWindow
    root.mainloop()         # Start the program loop until all windows exit

