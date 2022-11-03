from tkinter import *
import customtkinter
import os
from dotenv import load_dotenv
from functions import select_color, select_file, add_text, save, send_to_email

load_dotenv()

# Set sender email info here
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
PASSWORD = os.getenv('PASSWORD')
SMTP_SERVER = "smtp.gmail.com"

# Set up Tkinter GUI window
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
radiobutton_white = customtkinter.CTkRadioButton(master=window.frame, text="White text", variable=radio_var,
                                                 value="white", command=lambda: select_color(radio_var))
radiobutton_white.place(relx=0.26, rely=0.8, anchor=N)
radiobutton_white.select()
radiobutton_black = customtkinter.CTkRadioButton(master=window.frame, text="Black text ", variable=radio_var,
                                                 value="black", command=lambda: select_color(radio_var))
radiobutton_black.place(relx=0.262, rely=0.84, anchor=N)

# Slider
slider_label = customtkinter.CTkLabel(master=window.frame, text="Font size slider")
slider_label.place(relx=0.71, rely=0.795, anchor=N)
slider = customtkinter.CTkSlider(master=window.frame, from_=1, to=300)
slider.place(relx=0.71, rely=0.843, anchor=N)

# Buttons
upload_button = customtkinter.CTkButton(master=window.frame, text="Upload Image", width=150,
                                        command=lambda: select_file(canvas, entry))
upload_button.place(relx=0.3, rely=0.891, anchor=N)
watermark_button = customtkinter.CTkButton(master=window.frame, text="Add Watermark", width=150,
                                           command=lambda: add_text(entry, slider, canvas, radio_var))
watermark_button.place(relx=0.7, rely=0.891, anchor=N)
download_button = customtkinter.CTkButton(master=window.frame, text="Save Image", width=110,
                                          command=lambda: save(entry))
download_button.place(relx=0.16, rely=0.958, anchor=N)
send_to_email_button = customtkinter.CTkButton(master=window.frame, text="Send to Email", width=110,
                                               command=lambda: send_to_email(email_entry, entry, SENDER_EMAIL, PASSWORD, SMTP_SERVER))
send_to_email_button.place(relx=0.84, rely=0.958, anchor=N)

# Label
label = customtkinter.CTkLabel(master=window.frame, width=25, text="-or-")
label.place(relx=0.3, rely=0.975, anchor=CENTER)

window.mainloop()
