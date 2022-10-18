from tkinter import *
from tkinter import filedialog
import customtkinter
from PIL import Image, ImageTk, ImageFont, ImageDraw
import os
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import tempfile
from dotenv import load_dotenv
from downloads_folder_finder import get_download_folder

load_dotenv()

# Set sender email info here
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
PASSWORD = os.getenv('PASSWORD')
SMTP_SERVER = "smtp.gmail.com"


def select_color():
    if radio_var.get() == "black":
        return (0, 0, 0)
    else:
        return (255, 255, 255)


def select_file():
    """Opens filedialog, uploads selected JPEG or PNG file and displays it on canvas"""
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
    """Shows provided text on the canvas image"""
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
    """Saves the image with watermark to downloads folder"""
    try:
        # Timestamp for creating unique name
        image.save(fp=f'{get_download_folder()}/watermark_image_{time.time()}.{image.format}')
        # Notify user of saving image
        entry.delete(0, END)
        entry.insert(END, string="Image with watermark saved to the downloads folder")
    except NameError:
        # Notify user of not uploading the image
        entry.delete(0, END)
        entry.insert(END, string="No image selected. Upload your image first.")
    except ValueError:
        # Notify user of not uploading the image
        entry.delete(0, END)
        entry.insert(END, string="Reupload your image please.")


def send_to_email():
    """Sends the image with watermark to provided email address"""
    # Create a multipart message and set headers
    msg = MIMEMultipart()
    msg["Subject"] = "New Image from Watermark App!"
    msg["From"] = SENDER_EMAIL
    msg["To"] = email_entry.get()
    # Set message body text
    msg_text = MIMEText("Hello,\n\nthe image sent from Watermark App can be found in the attachment of this email.")
    msg.attach(msg_text)
    try:
        # Set image name and save it to temporary directory
        image_name = f"Watermark_image.{image.format}"
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, image_name)
        image.seek(0)
        try:
            image.save(file_path)
            image.close()
        except ValueError:
            entry.delete(0, END)
            entry.insert(END, string="Reupload your image please.")
            return
        # Attach selected image to the message
        with open(file_path, "rb") as selected_image:
            img = MIMEImage(selected_image.read())
            img.add_header('Content-Disposition', 'attachment', filename=image_name)
            msg.attach(img)
        # Send the message
        with smtplib.SMTP(SMTP_SERVER) as connection:
            connection.ehlo()
            connection.starttls()
            connection.login(user=SENDER_EMAIL, password=PASSWORD)
            try:
                connection.sendmail(
                    from_addr=SENDER_EMAIL,
                    to_addrs=email_entry.get(),
                    msg=msg.as_string()
                )
            except:
                entry.delete(0, END)
                entry.insert(END, string="No email address provided.")
    except NameError:
        entry.delete(0, END)
        entry.insert(END, string="No image selected. Upload your image first.")


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")

window = customtkinter.CTk()
window.title("Watermark App")
window.geometry("640x785")
window.minsize(width=620, height=785)
window.config(padx=40, pady=40)

# Frame
window.grid_columnconfigure(0, weight=1)
window.grid_rowconfigure(0, weight=1)
window.frame = customtkinter.CTkFrame(master=window, fg_color=None, height=705, width=540)
window.frame.pack()

# Canvas
canvas = Canvas(master=window.frame, width=500, height=500, highlightthickness=0, background="#C0C0C0")
canvas.place(relx=0.5, rely=0, anchor=N)

# Entry
entry = customtkinter.CTkEntry(master=window.frame, width=480)
entry.bind("<Button-1>", lambda e: entry.delete(0, END))
entry.insert(END, string="Type here your © copyright or other text to use as a watermark")
entry.place(relx=0.5, rely=0.735, anchor=N)
email_entry = customtkinter.CTkEntry(master=window.frame, width=208)
email_entry.bind("<Button-1>", lambda e: email_entry.delete(0, END))
email_entry.insert(END, string="Enter your email address here")
email_entry.place(relx=0.532, rely=0.958, anchor=N)

# Radio Buttons
radio_var = StringVar()
radiobutton_white = customtkinter.CTkRadioButton(master=window.frame, text="White text", command=select_color,
                                                 variable=radio_var, value="white")
radiobutton_white.place(relx=0.26, rely=0.8, anchor=N)
radiobutton_white.select()
radiobutton_black = customtkinter.CTkRadioButton(master=window.frame, text="Black text ", command=select_color,
                                                 variable=radio_var, value="black")
radiobutton_black.place(relx=0.262, rely=0.84, anchor=N)

# Slider
slider_label = customtkinter.CTkLabel(master=window.frame, text="Font size slider")
slider_label.place(relx=0.71, rely=0.795, anchor=N)
slider = customtkinter.CTkSlider(master=window.frame, from_=1, to=300)
slider.place(relx=0.71, rely=0.843, anchor=N)

# Buttons
upload_button = customtkinter.CTkButton(master=window.frame, text="Upload Image", width=150, command=select_file)
upload_button.place(relx=0.3, rely=0.891, anchor=N)
watermark_button = customtkinter.CTkButton(master=window.frame, text="Add Watermark", width=150, command=add_text)
watermark_button.place(relx=0.7, rely=0.891, anchor=N)
download_button = customtkinter.CTkButton(master=window.frame, text="Save Image", width=110, command=save)
download_button.place(relx=0.16, rely=0.958, anchor=N)
send_to_email_button = customtkinter.CTkButton(master=window.frame, text="Send to Email", width=110, command=send_to_email)
send_to_email_button.place(relx=0.84, rely=0.958, anchor=N)

# Label
label = customtkinter.CTkLabel(master=window.frame, width=25, text="-or-")
label.place(relx=0.3, rely=0.975, anchor=CENTER)

window.mainloop()
