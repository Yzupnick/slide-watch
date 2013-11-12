import glob 
import json
import os
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk, ImageOps
import time
import copy


SETTINGS_TEMPLATE = '{"default":{"timer":5000,"name":"Default"}}'
SETTINGS_FILE = "easyslide_settings.json"

class App():
    def __init__(self):
        self.root = tk.Tk()
        self.root.focus_set()
        self.root.bind("<Escape>", lambda e: e.widget.quit())
        self.path = tk.StringVar()
        self._set_up_main_screen()
        self.root.mainloop()

    def _set_up_main_screen(self):
        self.main_screen = ttk.Frame(self.root,padding=(10,10,10,10))
        ttk.Label(self.main_screen,text="Path to Folder of Slide Show").pack()
        ttk.Entry(self.main_screen,textvariable=self.path).pack()
        ttk.Button(self.main_screen,text="Start Slide Show",command=self.start_slide_show).pack()
        ttk.Button(self.main_screen,text="Modify Settings",command=self.modify_or_create_settings).pack()
        self.main_screen.pack()

    def _forget_main_screen(self):
        self.main_screen.pack_forget()

    def start_slide_show(self):
        self._forget_main_screen()
        self._set_up_show_screen()
        self._load_or_create_settings()
        self._load_slides()
        self.slide_index = 0
        self.update_slide()

    def update_slide(self):
        image_path = self.slides[self.slide_index]
        path,file_name = os.path.split(image_path)
        self.slide_index += 1
        if self.slide_index >= len(self.slides):
            self._load_or_create_settings()
            self._load_slides()
            self.slide_index = 0
        try:
            new_image = Image.open(image_path)
            new_image = ImageOps.fit(image=new_image,size=(self.screen_width,self.screen_height))
            old_image = self.current_image
            self.transition(old_image,new_image)
            if file_name not in self.settings:
                slide_length = self.settings["default"]["timer"].get()
            else:
                slide_length = self.settings[file_name]["timer"].get()
            self.root.after(slide_length, self.update_slide)
        except IOError:
            self.update_slide()

    def transition(self,image1,image2):
        transition_aplphas = (alpha/10.0 for alpha in range(1,11))
        for alpha in transition_aplphas:
            new_image = Image.blend(image1,image2,alpha)
            self.current_image = new_image
            tkpi = ImageTk.PhotoImage(self.current_image) 
            self.label_image.configure(image=tkpi)
            self.label_image.image = tkpi
            self.root.update_idletasks()

    def _set_up_show_screen(self):
        self.root.configure(cursor="none")
        self.root.attributes('-fullscreen', True)
        self.screen_width, self.screen_height = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry("%dx%d+0+0" % (self.screen_width, self.screen_height))
        self.label_image = tk.Label(self.root)
        self.label_image.configure()
        self.label_image.place(x=0,y=0,width=self.screen_width,height=self.screen_height)
        self.current_image = Image.new("RGB",(self.screen_width,self.screen_height))
        tkpi = ImageTk.PhotoImage(self.current_image) 
        self.label_image.configure(image=tkpi)
        self.label_image.image = tkpi
        self.label_image.pack()

    def _load_or_create_settings(self):
        if not os.path.isfile(self.path.get() + SETTINGS_FILE):
            self.create_settings_file()
        try:
            self.load_settings_file()
        except:
            self.create_settings_file()
            self.load_settings_file()

    def create_settings_file(self):
        with open(self.path.get() + SETTINGS_FILE,"w",encoding='utf-8') as setting_file:
                setting_file.write(SETTINGS_TEMPLATE)

    def load_settings_file(self):
        with open(self.path.get() + SETTINGS_FILE, encoding='utf-8') as json_data:
            self.settings = json.load(json_data)
            for key in self.settings:
                time = self.settings[key]["timer"]
                timeTCLVar = tk.IntVar()
                timeTCLVar.set(time)
                self.settings[key]["timer"] = timeTCLVar
                imageTCLVar = tk.StringVar()
                imageTCLVar.set(key)
                self.settings[key]["name"] = imageTCLVar


    def _load_slides(self):
        types = ("*.jpg","*.gif","*.png","*.jpeg","*.tiff","*.JPG","*.GIF","*.PNG","*.JPEG","*.TIFF")
        self.slides = []
        for files in types:
            self.slides.extend(glob.glob(self.path.get() + files))
        self.slides.sort()

    def modify_or_create_settings(self):
        options = ["default"] + os.listdir(self.path.get())
        self._load_or_create_settings()
        self._forget_main_screen()
        self.settings_screen = ttk.Frame(self.root)
        self._draw_settings_screen()

    def _draw_settings_screen(self):
        for child in self.root.winfo_children():
            child.pack_forget()

        ttk.Label(self.settings_screen,text=self.settings["default"]["name"].get()).grid(row=0,column=0)
        ttk.Entry(self.settings_screen,textvariable=str(self.settings["default"]["timer"])).grid(row=0,column=1)
        row = 1
        for key in self.settings:
            if key != "default":
                ttk.Label(self.settings_screen,text=self.settings[key]["name"].get()).grid(row=row,column=0)
                ttk.Entry(self.settings_screen,textvariable=str(self.settings[key]["timer"])).grid(row=row,column=1)
                ttk.Button(self.settings_screen,text="Delete",command= lambda: self._delete_setting(key)).grid(row=row,column=2)
                row += 1
        ttk.Button(self.settings_screen,text="Save",command= self.save_settings).grid(row=row,column=0)
        ttk.Button(self.settings_screen,text="Add Setting",command= self.add_setting).grid(row=row,column=2)
        self.settings_screen.pack()

    def _delete_setting(self,key):
        del self.settings[key]
        self._draw_settings_screen()

    def save_settings(self):
        with open(self.path.get() + SETTINGS_FILE,"w", encoding='utf-8') as setting_file:
            json_serialize = self.json_settings()
            setting_file.write(json_serialize)

    def set_path_dialog(self):
        self.path.set(filedialog.askdirectory("/") +"/")

    def new_setting_dialog(self):
        file_path = filedialog.askopenfilename(initialdir=self.path.get())
        path,filenname = os.path.split(file_path)
        return filenname



    def json_settings(self):
        json_string='{'
        for key in self.settings:
            json_string += '"{}":{{"timer":{}, "name":"{}"}},'.format(key,self.settings[key]["timer"].get(),self.settings[key]["name"].get())

        return json_string[0:-1] + "}"

    def add_setting(self):
        path,filename = os.path.split(self.new_setting_dialog())
        name = tk.StringVar()
        name.set(filename)
        time = tk.IntVar()
        time.set(self.settings["default"]["timer"].get())
        self.settings[filename] = {"name":name,"timer":time}
        self._draw_settings_screen()


            



app=App()
app.mainloop()