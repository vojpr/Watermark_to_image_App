from tkinter import *
from tkinter import filedialog
from tkmacosx import Button
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


def select_file():
    global resized_image, new_width, new_height, filename
    # Load image
    filetypes = (("image files", ('.png', '.jpg', '.jpeg')), ("all files", "*.*"))
    filename = filedialog.askopenfilename(title="Open a file", initialdir="/", filetypes=filetypes)
    img = Image.open(filename)
    # Resize image to fit 600x600 canvas (not saving the resized version)
    if img.height == img.width:
        new_height = 600
        new_width = 600
    elif img.height > img.width:
        new_height = 600
        new_width = img.width / (img.height / 600)
    elif img.height < img.width:
        new_height = img.height / (img.width / 600)
        new_width = 600
    resized_image = img.resize((int(new_width), int(new_height)), Image.LANCZOS)
    resized_image = ImageTk.PhotoImage(resized_image)
    # Show image on canvas
    canvas.config(width=int(new_width), height=int(new_height))
    canvas.create_image(new_width / 2, new_height / 2, image=resized_image)
    # Set text back after saving previous image
    entry.delete(0, END)
    entry.insert(END, string="Enter your © copyright ar other text to use as a watermark")


def add_text():
    global watermark_image, new_width, new_height, image
    # Get text, set font, open image
    text = entry.get()
    font = ImageFont.truetype("Arial Bold.ttf", 26)
    image = Image.open(filename)
    # Add watermark text
    edit_image = ImageDraw.Draw(image)
    edit_image.text((0, image.height / 2), text, (255, 255, 255), font=font)
    # Resize image to fit 600x600 canvas (not saving the resized version)
    watermark_image = image.resize((int(new_width), int(new_height)), Image.LANCZOS)
    watermark_image = ImageTk.PhotoImage(watermark_image)
    # Show watermark image on canvas
    canvas.create_image(new_width / 2, new_height / 2, image=watermark_image)


def save():
    # Save the image with watermark in original size
    # Timestamp for creating unique name
    image.save(fp=f'{get_download_folder()}/watermark_image_{time.time()}.jpg')
    # Notify user of saving image
    entry.delete(0, END)
    entry.insert(END, string="Image with watermark saved to the downloads folder")


window = Tk()
window.title("Watermark App")
window.config(background="#808080", padx=50, pady=50)

canvas = Canvas(window, width=600, height=600, highlightthickness=0, background="#C0C0C0")
canvas.grid(column=0, row=0, columnspan=5)

entry = Entry(width=52, highlightthickness=0)
entry.insert(END, string="Enter your © copyright ar other text to use as a watermark")
entry.grid(column=1, row=1, columnspan=3, pady=(5, 10))


upload_button = Button(text="Upload Image", bg='#77dd77', borderless=1, width=130, command=select_file)
upload_button.grid(column=1, row=3)
watermark_button = Button(text="Add Watermark", bg='#77dd77', borderless=1, width=130, command=add_text)
watermark_button.grid(column=2, row=3)
download_button = Button(text="Save Image", bg='#77dd77', borderless=1, width=130, command=save)
download_button.grid(column=3, row=3)

window.mainloop()
