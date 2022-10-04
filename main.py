from tkinter import *
from tkinter import filedialog
import customtkinter
from PIL import Image, ImageTk, ImageFont, ImageDraw
import os
import time

# Returns Downloads folder depending on operational system
if os.name == 'nt':
    import ctypes
    from ctypes import windll, wintypes
    from uuid import UUID

    # ctypes GUID copied from MSDN sample code
    class GUID(ctypes.Structure):
        _fields_ = [
            ("Data1", wintypes.DWORD),
            ("Data2", wintypes.WORD),
            ("Data3", wintypes.WORD),
            ("Data4", wintypes.BYTE * 8)
        ]

        def __init__(self, uuidstr):
            uuid = UUID(uuidstr)
            ctypes.Structure.__init__(self)
            self.Data1, self.Data2, self.Data3, \
            self.Data4[0], self.Data4[1], rest = uuid.fields
            for i in range(2, 8):
                self.Data4[i] = rest >> (8 - i - 1) * 8 & 0xff


    SHGetKnownFolderPath = windll.shell32.SHGetKnownFolderPath
    SHGetKnownFolderPath.argtypes = [
        ctypes.POINTER(GUID), wintypes.DWORD,
        wintypes.HANDLE, ctypes.POINTER(ctypes.c_wchar_p)
    ]


    def _get_known_folder_path(uuidstr):
        pathptr = ctypes.c_wchar_p()
        guid = GUID(uuidstr)
        if SHGetKnownFolderPath(ctypes.byref(guid), 0, 0, ctypes.byref(pathptr)):
            raise ctypes.WinError()
        return pathptr.value


    FOLDERID_Download = '{374DE290-123F-4565-9164-39C4925E467B}'


    def get_download_folder():
        return _get_known_folder_path(FOLDERID_Download)
else:
    def get_download_folder():
        home = os.path.expanduser("~")
        return os.path.join(home, "Downloads")


def select_color():
    if radio_var.get() == "black":
        return (0, 0, 0)
    else:
        return (255, 255, 255)


def select_file():
    global resized_image, new_width, new_height, filename
    # Load image
    filetypes = (("image files", ('.jpg', '.jpeg', '.png')), ("all files", "*.*"))
    filename = filedialog.askopenfilename(title="Open a file", initialdir="/", filetypes=filetypes)
    try:
        img = Image.open(filename)
        # Resize image to fit 500x500 canvas (not saving the resized version)
        if img.height == img.width:
            new_height = 500
            new_width = 500
        elif img.height > img.width:
            new_height = 500
            new_width = img.width / (img.height / 500)
        elif img.height < img.width:
            new_height = img.height / (img.width / 500)
            new_width = 500
        resized_image = img.resize((int(new_width), int(new_height)), Image.Resampling.LANCZOS)
        resized_image = ImageTk.PhotoImage(resized_image)
        # Show image on canvas
        canvas.config(width=int(new_width), height=int(new_height))
        canvas.create_image(new_width / 2, new_height / 2, image=resized_image)
        # Set text back after saving previous image
        entry.delete(0, END)
        entry.insert(END, string="Enter your © copyright ar other text to use as a watermark")
    except AttributeError:
        return


def add_text():
    global watermark_image, new_width, new_height, image
    # Get text, set font, open image
    text = entry.get()
    font = ImageFont.truetype("Arial Bold.ttf", int(slider.get()))
    try:
        image = Image.open(filename)
        # Add watermark text
        edit_image = ImageDraw.Draw(image)
        edit_image.text((0, image.height / 2), text, fill=select_color(), font=font)
        # Resize image to fit 500x500 canvas (not saving the resized version)
        watermark_image = image.resize((int(new_width), int(new_height)), Image.Resampling.LANCZOS)
        watermark_image = ImageTk.PhotoImage(watermark_image)
        # Show watermark image on canvas
        canvas.create_image(new_width / 2, new_height / 2, image=watermark_image)
    except NameError:
        # Notify user of not uploading the image
        entry.delete(0, END)
        entry.insert(END, string="No image selected. Upload your image first.")
    except AttributeError:
        # Notify user of missing image
        entry.delete(0, END)
        entry.insert(END, string="Reupload your image please.")


def save():
    # Save the image with watermark in original size
    try:
        # Timestamp for creating unique name
        try:
            image.save(fp=f'{get_download_folder()}/watermark_image_{time.time()}.jpg')
        except OSError:
            image.save(fp=f'{get_download_folder()}/watermark_image_{time.time()}.png')
        # Notify user of saving image
        entry.delete(0, END)
        entry.insert(END, string="Image with watermark saved to the downloads folder")
    except NameError:
        # Notify user of not uploading the image
        entry.delete(0, END)
        entry.insert(END, string="No image selected. Upload your image first.")


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")

window = customtkinter.CTk()
window.title("Watermark App")
window.geometry("640x740")
window.config(padx=40, pady=40)

# Frame
window.grid_columnconfigure(0, weight=1)
window.grid_rowconfigure(0, weight=1)
window.frame = customtkinter.CTkFrame(master=window, fg_color=None)
window.frame.grid(row=0, column=0)

# Canvas
canvas = Canvas(master=window.frame, width=500, height=500, highlightthickness=0, background="#C0C0C0")
canvas.grid(column=0, row=0, columnspan=6)

# Entry
entry = customtkinter.CTkEntry(master=window.frame, width=480)
entry.insert(END, string="Type here your © copyright or other text to use as a watermark")
entry.grid(column=0, row=1, columnspan=6, pady=(15, 0))

# Radio Buttons
radio_var = StringVar()
radiobutton_white = customtkinter.CTkRadioButton(master=window.frame, text="White text", command=select_color,
                                                 variable=radio_var, value="white")
radiobutton_white.grid(column=0, row=2, columnspan=3, pady=(15, 0))
radiobutton_white.select()
radiobutton_black = customtkinter.CTkRadioButton(master=window.frame, text="Black text ", command=select_color,
                                                 variable=radio_var, value="black")
radiobutton_black.grid(column=0, row=3, columnspan=3, pady=(3, 0))

# Slider
slider_label = customtkinter.CTkLabel(master=window.frame, text="Font size slider")
slider_label.grid(column=3, row=2, columnspan=3, pady=(15, 0))
slider = customtkinter.CTkSlider(master=window.frame, from_=1, to=300)
slider.grid(column=3, row=3, columnspan=3)

# Buttons
upload_button = customtkinter.CTkButton(master=window.frame, text="Upload Image", width=130, command=select_file)
upload_button.grid(column=0, row=4, columnspan=2, pady=(15, 0))
watermark_button = customtkinter.CTkButton(master=window.frame, text="Add Watermark", width=130, command=add_text)
watermark_button.grid(column=2, row=4, columnspan=2, pady=(15, 0))
download_button = customtkinter.CTkButton(master=window.frame, text="Save Image", width=130, command=save)
download_button.grid(column=4, row=4, columnspan=2, pady=(15, 0))

window.mainloop()
