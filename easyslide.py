import glob 
import json
import os
import tkinter as tk
from PIL import Image, ImageTk, ImageOps
import time

class App():
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("%dx%d+0+0" % (200, 200))
        self.root.focus_set()
        self.root.bind("<Escape>", lambda e: e.widget.quit())
        self.path_label = tk.Label(self.root,text="Path to Folder of Slide Show")
        self.path_label.pack()
        self.path_text = tk.Entry(self.root)
        self.path_text.pack()
        self.start_slide_show_button = tk.Button(self.root,text="Start Slide Show",command=self.start_slide_show)
        self.start_slide_show_button.pack()
        self.root.mainloop()

    def start_slide_show(self):
        self.path = self.path_text.get()
        self._forget_open_window()
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
            image = Image.open(image_path)
            image = ImageOps.fit(image=image,size=(self.screen_width,self.screen_height))
            tkpi = ImageTk.PhotoImage(image) 
            self.label_image.configure(image=tkpi)
            self.label_image.image = tkpi
            if file_name not in self.settings:
                slide_length = self.settings["default"]["timer"]
            else:
                slide_length = self.settings[file_name]["timer"]
            self.root.after(slide_length, self.update_slide)
        except IOError:
            self.update_slide()

    def _forget_open_window(self):
        self.start_slide_show_button.pack_forget()
        self.path_label.pack_forget()
        self.path_text.pack_forget()

    def _set_up_show_screen(self):
        self.root.configure(cursor="none")
        self.root.attributes('-fullscreen', True)
        self.screen_width, self.screen_height = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry("%dx%d+0+0" % (self.screen_width, self.screen_height))
        self.label_image = tk.Label(self.root)
        self.label_image.configure(background='black')
        self.label_image.place(x=0,y=0,width=self.screen_width,height=self.screen_height)
        self.label_image.pack()

    def _load_or_create_settings(self):
        json_data=open(self.path + "easyslide_settings.json")
        self.settings = json.load(json_data)
        json_data.close()

    def _load_slides(self):
        types = ("*.jpg","*.gif","*.png","*.jpeg","*.tiff","*.JPG","*.GIF","*.PNG","*.JPEG","*.TIFF")
        self.slides = []
        for files in types:
            self.slides.extend(glob.glob(self.path + files))

app=App()
app.mainloop()