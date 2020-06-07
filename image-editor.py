# System package imports
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog, simpledialog
import os
import pickle
# 3rd party package imports
from PIL import Image, ImageTk, ImageDraw, ImageFont
# Project imports
import app

ALLOWED_FILES = (("JPEG files","*.jpg"),("PNG files","*.png"),("all files","*.*"))
IMAGE_FRAME_BACKGROUND = "gray95"
TOOLS_BACKGROUND = "gray90"
SETTINGS_FILE = "image-editor-settings.pickle"
SUPPORTED_IMAGE_EXTENSIONS = ("jpg", "jpeg", "png")

class AppWindow():
    def __init__(self, parent):
        # Create the window
        self.parent = parent                # Save a reference to our parent object
        self.window = tk.Toplevel()         # Create a window
        self.window.geometry("1200x700")     # Set pixel dimensions 400 wide by 200 high
        self.window.title("pbTools image editor")       # Set window title text
        self.window.state('zoomed')         # Maximise window
        self.window.protocol("WM_DELETE_WINDOW", self.window.quit) # Enable the close icon
        self.window.update() # https://stackoverflow.com/a/49216638/10971929
        dimensions = (max(1200,self.window.winfo_width()), max(700,self.window.winfo_height()))
        print(f"Window size: {dimensions}")
        # Image display area...
        self.image_frame = tk.Frame(self.window)
        self.image_frame.place(x=54, y=0, width=dimensions[0]-54, height=dimensions[1]-100)
        self.image_frame.config(background=IMAGE_FRAME_BACKGROUND) # colour names @ http://www.science.smith.edu/dftwiki/images/3/3d/TkInterColorCharts.png
        self.image_frame.update()
        frame_size = (self.image_frame.winfo_width(), self.image_frame.winfo_height())
        self.image_container = tk.Label(self.image_frame, text="", bg=IMAGE_FRAME_BACKGROUND)
        self.image_container.place(x=0, y=0, width=frame_size[0], height=frame_size[1])
        # Toolbars and property frames...
        self.toolbar_frame = tk.Frame(self.window)
        self.toolbar_frame.place(x=0, y=0, width=54, height=dimensions[1])
        self.toolbar_frame.config(background=TOOLS_BACKGROUND)
        self.toolsettings_frame = tk.Frame(self.window)
        self.toolsettings_frame.place(x=0, y=dimensions[1]-100, width=dimensions[0]-216, height=100)
        self.toolsettings_frame.config(background=TOOLS_BACKGROUND)
        self.bottombar_frame = tk.Frame(self.window)
        self.bottombar_frame.place(x=dimensions[0]-216, y=dimensions[1]-100, width=216, height=54)
        self.bottombar_frame.config(background=TOOLS_BACKGROUND)
        self.properties_frame = tk.Frame(self.window)
        self.properties_frame.place(x=dimensions[0]-216, y=dimensions[1]-48, width=216, height=48)
        self.properties_frame.config(background=TOOLS_BACKGROUND)
        self.load_assets()
        self.generate_menu()
        self.generate_toolbar(self.toolbar_frame)
        self.generate_bottombar(self.bottombar_frame)
        # Initalise working variables...
        self.filename = ""
        self.fileopen = False
        self.dirty = False
        self.image = None       # The PIL image object
        self.imageTk = None     # The PIL imagetk object (note: self.image will be authoritative)
        self.properties = {}    # Information about the open file
        self.settings = {}      # Application settings (default behaviours etc)
        self.settings['default_folder'] = os.curdir
        self.load_settings()
        self.history = []
        self.active_tool = ""
        self.active_tool_data = {}
        # Key bindings
        self.window.bind('<Left>', self.file_previous)
        self.window.bind('<Right>', self.file_next)
        self.window.bind_all('<Control-Key-z>', self.undo)
        self.window.bind_all('<Control-Key-s>', self.file_save)
        self.window.bind('<Control-Key-r>', self.rotate_right)
        self.window.bind('<Control-Key-c>', self.crop)
        self.window.bind('<Key-a>', self.crop)
        self.window.bind('<Key-s>', self.crop)
        self.window.bind('<Key-d>', self.crop)
        self.window.bind('<Key-w>', self.crop)
        self.window.bind('<Key-plus>', self.crop)
        self.window.bind('<Key-minus>', self.crop)
        self.window.bind('<Return>', self.crop)
        # Open most recent file
        if "most_recent" in self.settings:
            self.file_open(self.settings['most_recent'])

    def get_images_in_folder(self, folder):
        files = os.listdir(folder)
        image_files = []
        for f in files:
            extension = f.split(".")[-1]
            if extension.lower() in SUPPORTED_IMAGE_EXTENSIONS:
                image_files.append(f)
        return image_files

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "rb") as f:
                    self.settings = pickle.load(f)
            except:
                print(f"Error reading {SETTINGS_FILE}. Invalid content?")

    def save_settings(self):
        with open(SETTINGS_FILE, "wb") as f:
            pickle.dump(self.settings, f)
    
    def load_assets(self):
        self.icons = {
            "previous" : tk.PhotoImage(file="assets/icons8-back-50.png"),
            "crop" : tk.PhotoImage(file="assets/icons8-crop-50.png"),
            "delete" : tk.PhotoImage(file="assets/icons8-delete-bin-50.png"),
            "erase" : tk.PhotoImage(file="assets/icons8-erase-50.png"),
            "fill-color" : tk.PhotoImage(file="assets/icons8-fill-color-50.png"),
            "next" : tk.PhotoImage(file="assets/icons8-forward-50.png"),
            "line" : tk.PhotoImage(file="assets/icons8-line-50.png"),
            "ellipse" : tk.PhotoImage(file="assets/icons8-oval-50.png"),
            "paint" : tk.PhotoImage(file="assets/icons8-paint-palette-50.png"),
            "pen" : tk.PhotoImage(file="assets/icons8-pen-50.png"),
            "rectangle" : tk.PhotoImage(file="assets/icons8-rectangular-50.png"),
            "resize" : tk.PhotoImage(file="assets/icons8-resize-50.png"),
            "save" : tk.PhotoImage(file="assets/icons8-save-50.png"),
            "text" : tk.PhotoImage(file="assets/icons8-text-box-50.png"),
            "rotate-left" : tk.PhotoImage(file="assets/icons8-rotate-left-50.png"),
            "rotate-right" : tk.PhotoImage(file="assets/icons8-rotate-right-50.png")
        }

    def generate_toolbar(self, target):
        self.toolbar_buttons = [
            tk.Button(target, text="Resize", command=self.resize, image=self.icons['resize'], state=tk.DISABLED, bg="gray50"),
            tk.Button(target, text="Crop", command=self.crop, image=self.icons['crop']),
            tk.Button(target, text="Rotate right", command=self.rotate_right, image=self.icons['rotate-right']),
            tk.Button(target, text="Rotate left", command=self.rotate_left, image=self.icons['rotate-left']),
            tk.Button(target, text="Text", command=self.text, image=self.icons['text'], state=tk.DISABLED),
            tk.Button(target, text="Pen", command=self.pen, image=self.icons['pen'], state=tk.DISABLED),
            tk.Button(target, text="Line", command=self.line, image=self.icons['line'], state=tk.DISABLED),
            tk.Button(target, text="Rectangle", command=self.rectangle, image=self.icons['rectangle'], state=tk.DISABLED),
            tk.Button(target, text="Elipse", command=self.elipse, image=self.icons['ellipse'], state=tk.DISABLED),
            tk.Button(target, text="Erase", command=self.erase, image=self.icons['erase'], state=tk.DISABLED),
            tk.Button(target, text="Foreground", command=self.setforeground, image=self.icons['fill-color'], state=tk.DISABLED),
            tk.Button(target, text="Background", command=self.setbackground, image=self.icons['paint'], state=tk.DISABLED)
        ]
        for i in range(len(self.toolbar_buttons)):
            self.toolbar_buttons[i].grid(row=i, column=0, sticky='nesw')
    
    def generate_bottombar(self, target):
        self.toolbar_buttons = [
            tk.Button(target, text="Previous", command=self.file_previous, image=self.icons['previous']),
            tk.Button(target, text="Save", command=self.file_save, image=self.icons['save']),
            tk.Button(target, text="Delete", command=self.file_delete, image=self.icons['delete']),
            tk.Button(target, text="Next", command=self.file_next, image=self.icons['next']),
        ]
        for i in range(len(self.toolbar_buttons)):
            self.toolbar_buttons[i].grid(row=0, column=i, sticky='e')
    
    def generate_menu(self):
        # Create a menu bar
        menubar = tk.Menu(self.window)
        # Create a sub menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.file_open)
        filemenu.add_command(label="Save (ctrl-s)", command=self.file_saveas)
        filemenu.add_command(label="Save as", command=self.file_saveas)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.window.quit)
        # Create a sub menu
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo (ctrl-z)", command=self.undo)
        editmenu.add_command(label="Revert", command=self.revert)
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
    
    def show_properties(self):
        # Display key information about the current image file
        if self.filename != "":
            filename_parts = self.filename.split("/")
            filename_display = filename_parts[ -1 ]
            self.properties_filename_label = tk.Label(self.properties_frame, text=f"File: {filename_display}                              ", font=('Arial', 12), bg=TOOLS_BACKGROUND, justify=tk.LEFT) 
            self.properties_dimensions_label = tk.Label(self.properties_frame, text=f"Dimensions: {self.properties['dimensions'][0]} x {self.properties['dimensions'][1]}, Mode: {self.properties['mode']}                    ", font=('Arial', 12), bg=TOOLS_BACKGROUND, justify=tk.LEFT) 
            self.properties_filename_label.place(x=0,y=0)
            self.properties_dimensions_label.place(x=0,y=20)
            self.window.title("pbTools image editor - "+filename_display)
    
    def show_image(self, image=None):
        # Render a PIL image object to the image_frame
        if image is None:
            image = self.image
        if image is None:
            return False
        self.image_frame.update()
        frame_size = (self.image_frame.winfo_width(), self.image_frame.winfo_height())
        frame_ratio = frame_size[0] / frame_size[1] # 1.9 wide for every height 1146 600
        image_ratio = image.size[0] / image.size[1] # 1.5 wide for every height 2480 1653 ... 900 600
        if frame_ratio > image_ratio:
            # Scale to fill vertically, empty space on the horizontal
            image_scaled = image.resize((int(frame_size[1] * image_ratio), frame_size[1]))
        else:
            # Scale to fill horizontally, empty space on the vertical
            image_scaled = image.resize((frame_size[0], int(frame_size[0] / image_ratio)))
        self.properties['frame'] = frame_size
        self.properties['dimensions'] = image.size
        self.properties['frame_ratio'] = frame_ratio
        self.properties['image_ratio'] = image_ratio
        self.properties['scaled_size'] = image_scaled.size
        self.properties['scale_ratio'] = image.size[0] / image_scaled.size[0]
        self.properties['offset'] = (int(frame_size[0]/2 - image_scaled.size[0]/2), int(frame_size[1]/2 - image_scaled.size[1]/2))
        self.imageTk = ImageTk.PhotoImage(image_scaled)
        self.image_container.configure(image=self.imageTk)
        self.show_properties()

    def file_open(self, filename=None):
        if filename is None or filename == "":
            filename = filedialog.askopenfilename(initialdir=self.settings['default_folder'], title="Select file", filetypes=ALLOWED_FILES)
        if os.path.exists(filename) and os.path.isfile(filename):
            try:
                self.image = Image.open(filename)
            except:
                messagebox.showerror("Sorry", f"Unable to open {filename}. Possibly not an image file? or permissions error?")
                return False
            filename_parts = filename.split("/")
            if len(filename_parts) > 1:
                del filename_parts[ -1 ]
                folder = "/".join(filename_parts)
                self.settings['default_folder'] = folder
            self.settings['most_recent'] = filename
            self.save_settings()
            self.properties['dimensions'] = self.image.size
            self.properties['mode'] = self.image.mode
            self.filename = filename
            self.show_properties()
            self.show_image()
            self.history = []
            self.dirty = False
            self.fileopen = True
    
    def file_save(self, event=None):
        if self.dirty:
            parts = self.filename.split(".")
            if 'convert_all_to' in self.settings:
                ext = self.settings['convert_all_to']
                parts[-1] = ext
            new_filename = ".".join(parts)
            if parts[-1].lower() in ("jpg", "jpeg"):
                self.image.save(new_filename,"jpeg")
                self.dirty = False
            elif parts[-1].lower() in ("png"):
                self.image.save(new_filename,"png")
                self.dirty = False

    def file_saveas(self):
        filename = filedialog.asksaveasfilename(initialdir=self.default_folder, title="Select file", filetypes=ALLOWED_FILES)

    def file_next(self, event=None): # The event is received if executed via the key binding
        if self.dirty:
            if messagebox.askyesno("Changes made", f"Save changes to {self.filename}?"):
                self.file_save()
        images_in_folder = self.get_images_in_folder(self.settings['default_folder'])
        images_in_folder.sort()
        image_number = -1
        for i in range(len(images_in_folder)):
            if self.filename.split("/")[-1] == images_in_folder[i]:
                image_number = i
        if image_number >= 0:
            image_number = (image_number + 1) % len(images_in_folder)
            print(f"Opening {images_in_folder[image_number]}")
            self.file_open(self.settings['default_folder']+"/"+images_in_folder[image_number])
        else:
            self.file_open("")

    def file_delete(self):
        if self.fileopen:
            confirm = messagebox.askyesno("Confirm file delete?", f"Delete file {self.filename}?")
            if confirm:
                os.remove(self.filename)
                del self.settings['most_recent']
                self.dirty = False
                self.fileopen = False
                self.filename = ""
                self.image = None
                self.imageTk = None
                self.image_container.configure(image=None)
                self.show_properties()
        else:
            messagebox.showerror("I'm confused", "No file open")

    def file_previous(self, event=None):  # The event is received if executed via the key binding
        if self.dirty:
            if messagebox.askyesno("Changes made", f"Save changes to {self.filename}?"):
                self.file_save()
        images_in_folder = self.get_images_in_folder(self.settings['default_folder'])
        images_in_folder.sort()
        image_number = -1
        for i in range(len(images_in_folder)):
            if self.filename.split("/")[-1] == images_in_folder[i]:
                image_number = i
        if image_number >= 0:
            image_number = (image_number - 1) % len(images_in_folder)
            print(f"Opening {images_in_folder[image_number]}")
            self.file_open(self.settings['default_folder']+"/"+images_in_folder[image_number])
        else:
            self.file_open("")

    def about(self):
        about = app.AboutWindow(self.window)
    
    def resize(self):
        messagebox.showerror("Sorry", "Feature not yet implemented :-/")

    def crop_attempt_1(self, event=None): # Mouse control
        # Default crop is 1:1 ratio
        if 'crop_ratio' in self.settings:
            ratio = self.settings['crop_ratio']
        elif 'ratio' in self.active_tool_data:
            ratio = self.active_tool_data['ratio']
        else:
            ratio = 1.0
        if event is not None and self.active_tool == "crop":
            left_edge = self.properties['offset'][0]
            right_edge = self.properties['offset'][0] + self.properties['scaled_size'][0]
            top_edge = self.properties['offset'][1]
            bottom_edge = self.properties['offset'][1] + self.properties['scaled_size'][1]
            if str(event.type) == "ButtonPress":
                print('ButtonPress',event.x, event.y)
                self.add_to_history()
                self.active_tool_data['crop_start_x'] = int((max(min(event.x, right_edge), left_edge) - left_edge) * self.properties['scale_ratio'])
                self.active_tool_data['crop_start_y'] = int((max(min(event.y, bottom_edge), top_edge) - top_edge) * self.properties['scale_ratio'])
                draw = ImageDraw.Draw(self.image, 'RGBA')
                draw.rectangle((0,0,self.properties['dimensions'][0],self.active_tool_data['crop_start_y']-1), fill="#00000080")
                draw.rectangle((0,0,self.active_tool_data['crop_start_x']-1,self.properties['dimensions'][1]), fill="#00000080")
                self.dirty = True
                self.active_tool_data['ButtonPress'] = True
                print(self.active_tool_data)
            elif str(event.type) == "ButtonRelease" and 'ButtonPress' in self.active_tool_data:
                print('ButtonRelease',event.x, event.y)
                self.active_tool_data['crop_end_x'] = int((max(min(event.x, right_edge), left_edge) - left_edge) * self.properties['scale_ratio'])
                self.active_tool_data['crop_end_y'] = int((max(min(event.y, bottom_edge), top_edge) - top_edge) * self.properties['scale_ratio'])
                print(self.active_tool_data)
                w = self.active_tool_data['crop_end_x'] - self.active_tool_data['crop_start_x']
                h = self.active_tool_data['crop_end_y'] - self.active_tool_data['crop_start_y']
                if w > h:
                    self.active_tool_data['crop_end_y'] = self.active_tool_data['crop_start_y'] + int(w * ratio)
                else:
                    self.active_tool_data['crop_end_x'] = self.active_tool_data['crop_start_x'] + int(h / ratio)
                print(self.active_tool_data)
                if self.active_tool_data['crop_start_x'] < self.active_tool_data['crop_end_x'] and self.active_tool_data['crop_start_y'] < self.active_tool_data['crop_end_y']:
                    print("Cropping...")
                    self.image = self.image.crop((self.active_tool_data['crop_start_x'], 
                        self.active_tool_data['crop_start_y'], 
                        self.active_tool_data['crop_end_x'], 
                        self.active_tool_data['crop_end_y']))
                else:
                    print("Zero area selected, aborting crop...")
                    self.undo()
                self.active_tool = ""
                self.active_tool_data = {}
                self.window.bind('<Button-1>', None)
                self.window.bind('<ButtonRelease-1>', None)
            print("Showing image...")
            self.show_image()
        elif event is None:
            print('Crop button')
            self.window.bind('<Button-1>', self.crop)
            self.window.bind('<ButtonRelease-1>', self.crop)
            self.active_tool = "crop"
            self.active_tool_data = {}

    def crop(self, event=None): # Keyboard control
        def add_crop_mask(image, x,y,w,h): # Coordinates as per original image not the scaled image on display
            print(x,y,w,h, image.size[0], image.size[1])
            draw = ImageDraw.Draw(image, 'RGBA')
            draw.rectangle((0,0,image.size[0],y), fill="#00000080") # Top
            draw.rectangle((0,y,x,y+h), fill="#00000080") # Left
            draw.rectangle((x+w,y,image.size[0],y+h), fill="#00000080") # Right
            draw.rectangle((0,y+h,image.size[0],image.size[1]), fill="#00000080") # Bottom
        # Default crop is 1:1 ratio 
        if 'crop_ratio' in self.settings:
            ratio = self.settings['crop_ratio']
        elif 'ratio' in self.active_tool_data:
            ratio = self.active_tool_data['ratio']
        else:
            ratio = 1.0 # One x for every one y. Ratio > 1 are wider, ratio < 1 are taller
        # How many pixels to move for each key press
        if 'crop_step' in self.settings:
            step = self.settings['crop_step']
        elif 'step' in self.active_tool_data:
            step = self.active_tool_data['step']
        else:
            step = int(self.image.size[0]/20.0)
        # Crop button has been pressed on toolbar
        # or Control-C key combination (event.state==4 is Control)
        if event is None or (str(event.type)=="KeyPress" and event.state==4 and event.keysym=="c"): 
            print('Crop button')
            self.add_to_history()
            self.dirty = True
            if self.image.size[0] > self.image.size[1]: # Image is landscape orientation
                y = 0
                h = self.image.size[1] # Full height
                w = int( h * ratio )
                x = int(self.image.size[0] / 2) - int(w/2)
            else: # Image is portrait orientation
                x = 0
                w = self.image.size[0] # Full width
                h = int( w * ratio )
                y = int(self.image.size[1] / 2) - int(h/2)
            self.active_tool = "crop"
            self.active_tool_data = {'x':x, 'y':y, 'w':w, 'h':h}
            self.crop_tool_original_image = self.image.copy()
            add_crop_mask(self.image, self.active_tool_data['x'],self.active_tool_data['y'],self.active_tool_data['w'],self.active_tool_data['h'])
            self.show_image()
        elif event is not None and self.active_tool == "crop": # Key press
            print(event)
            if str(event.type) == "KeyPress" and event.char == 'a': # Move left
                if self.active_tool_data['x'] > step:
                    self.active_tool_data['x'] -= step
                else:
                    self.active_tool_data['x'] = 0
                self.image = self.crop_tool_original_image.copy()
                add_crop_mask(self.image, self.active_tool_data['x'],self.active_tool_data['y'],self.active_tool_data['w'],self.active_tool_data['h'])
            elif str(event.type) == "KeyPress" and event.char == 's': # Move down
                if self.active_tool_data['y']+self.active_tool_data['h']+step < self.image.size[1]:
                    self.active_tool_data['y'] += step
                else:
                    self.active_tool_data['y'] = self.image.size[1] - self.active_tool_data['h']
                self.image = self.crop_tool_original_image.copy()
                add_crop_mask(self.image, self.active_tool_data['x'],self.active_tool_data['y'],self.active_tool_data['w'],self.active_tool_data['h'])
            elif str(event.type) == "KeyPress" and event.char == 'd': # Move right
                if self.active_tool_data['x']+self.active_tool_data['w']+step < self.image.size[0]:
                    self.active_tool_data['x'] += step
                else:
                    self.active_tool_data['x'] = self.image.size[0] - self.active_tool_data['w']
                self.image = self.crop_tool_original_image.copy()
                add_crop_mask(self.image, self.active_tool_data['x'],self.active_tool_data['y'],self.active_tool_data['w'],self.active_tool_data['h'])
            elif str(event.type) == "KeyPress" and event.char == 'w': # Move up
                if self.active_tool_data['y'] > step:
                    self.active_tool_data['y'] -= step
                else:
                    self.active_tool_data['y'] = 0
                self.image = self.crop_tool_original_image.copy()
                add_crop_mask(self.image, self.active_tool_data['x'],self.active_tool_data['y'],self.active_tool_data['w'],self.active_tool_data['h'])
            elif str(event.type) == "KeyPress" and event.keysym == 'plus': # Increase selection size
                if self.active_tool_data['w'] < self.image.size[0] and self.active_tool_data['h'] < self.image.size[1]:
                    self.active_tool_data['w'] += step
                    self.active_tool_data['h'] = self.active_tool_data['w'] / ratio
                self.image = self.crop_tool_original_image.copy()
                add_crop_mask(self.image, self.active_tool_data['x'],self.active_tool_data['y'],self.active_tool_data['w'],self.active_tool_data['h'])
            elif str(event.type) == "KeyPress" and event.keysym == 'minus': # Decrease selection size
                if self.active_tool_data['w'] > 2*step and self.active_tool_data['h'] > 2*step:
                    self.active_tool_data['w'] -= step
                    self.active_tool_data['h'] = self.active_tool_data['w'] / ratio
                self.image = self.crop_tool_original_image.copy()
                add_crop_mask(self.image, self.active_tool_data['x'],self.active_tool_data['y'],self.active_tool_data['w'],self.active_tool_data['h'])
            elif str(event.type) == "KeyPress" and event.keysym == "Return": # Finalise the cropping
                self.image = self.crop_tool_original_image.copy()
                self.image = self.image.crop((self.active_tool_data['x'],self.active_tool_data['y'],self.active_tool_data['x']+self.active_tool_data['w'],self.active_tool_data['y']+self.active_tool_data['h']))
                self.active_tool = ""
                self.active_tool_data = {}
            self.show_image()

    def rotate_left(self):
        if self.image is not None:
            self.add_to_history()
            self.image = self.image.rotate(90, expand=True)
            self.dirty = True
            self.show_image()

    def rotate_right(self, event=None):
        if self.image is not None:
            self.add_to_history()
            self.image = self.image.rotate(-90, expand=True)
            self.dirty = True
            self.show_image()
    
    def text(self):
        messagebox.showerror("Sorry", "Feature not yet implemented :-/")

    def pen(self):
        messagebox.showerror("Sorry", "Feature not yet implemented :-/")

    def line(self):
        messagebox.showerror("Sorry", "Feature not yet implemented :-/")

    def rectangle(self):
        messagebox.showerror("Sorry", "Feature not yet implemented :-/")

    def elipse(self):
        messagebox.showerror("Sorry", "Feature not yet implemented :-/")

    def erase(self):
        messagebox.showerror("Sorry", "Feature not yet implemented :-/")

    def setforeground(self):
        messagebox.showerror("Sorry", "Feature not yet implemented :-/")

    def setbackground(self):
        messagebox.showerror("Sorry", "Feature not yet implemented :-/")

    def undo(self, event=None):
        if len(self.history) > 0:
            self.image = self.history.pop(-1)
            self.show_image()
        if len(self.history) == 0:
            self.dirty = False

    def add_to_history(self):
        self.history.append(self.image.copy())

    def revert(self):
        messagebox.showerror("Sorry", "Feature not yet implemented :-/")
        while len(self.history) > 0:
            self.undo()

if __name__ == "__main__":
    root = tk.Tk()          # Initialise the tk system into an object called `root`
    root.withdraw()         # Hide the default window
    main = AppWindow(root)   # Run our window, called AppWindow
    root.mainloop()         # Start the program loop until all windows exit

