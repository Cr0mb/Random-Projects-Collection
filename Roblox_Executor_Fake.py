# fake roblox executor, can be used to hide background tasks

import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import os
import random
import time
import threading
import zipfile
import subprocess
import sys
import shutil
import json
import base64
import sqlite3
import queue
import socket
import platform
import winreg
import uuid

import psutil
import pyperclip
from pynput.keyboard import Listener
from Crypto.Cipher import AES
import win32crypt
import requests
from PIL import Image, ImageTk

github_image_url = "https://raw.githubusercontent.com/X-Rex360/Fetch/main/background1.jpg"
downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
background_path = os.path.join(downloads_folder, "background.png")

def download_background():
    try:
        response = requests.get(github_image_url, stream=True)
        response.raise_for_status()
        with open(background_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print("\n")
    except Exception as e:
        print(f"\n")

download_background()

def update_file_list(directory):
    file_listbox.delete(0, tk.END)
    for file in os.listdir(directory):
        if file.endswith(".lua"):
            file_listbox.insert(tk.END, file)

def execute_script():
    popup = tk.Toplevel(root)
    popup.title("Executing")
    popup.geometry("300x100")
    tk.Label(popup, text="Waiting on Roblox to be opened..", font=("Arial", 12)).pack(pady=20)

def clear_script():
    text_editor.delete("1.0", tk.END)

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Lua Files", "*.lua")])
    if file_path and file_path.endswith(".lua"):
        with open(file_path, "r") as file:
            text_editor.delete("1.0", tk.END)
            text_editor.insert("1.0", file.read())
        directory = os.path.dirname(file_path)
        update_file_list(directory)
    else:
        messagebox.showerror("Error", "Only .lua files are allowed!")

def inject():
    messagebox.showinfo("Inject", "Injection successful (simulation)")

def load_selected_file(event):
    try:
        selected_index = file_listbox.curselection()
        if not selected_index:
            return
        selected_file = file_listbox.get(selected_index)
        script_directory = os.path.dirname(filedialog.askopenfilename())
        file_path = os.path.join(script_directory, selected_file)
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                text_editor.delete("1.0", tk.END)
                text_editor.insert("1.0", file.read())
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load file: {e}")

root = tk.Tk()
root.title("Roblox Executor")
root.geometry("650x400")
root.attributes('-alpha', 0.9)

if os.path.exists(background_path):
    bg_image = Image.open(background_path)
    bg_image = bg_image.resize((650, 400), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(relwidth=1, relheight=1)
else:
    print("\n")

sidebar = tk.Frame(root, bg="#2C2F33", width=150)
sidebar.pack(side=tk.LEFT, fill=tk.Y)

file_listbox = tk.Listbox(sidebar, bg="#23272A", fg="white", selectbackground="#7289DA")
file_listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
file_listbox.bind("<<ListboxSelect>>", load_selected_file)

text_editor = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15, width=58, bg="#23272A", fg="white")
text_editor.pack(pady=10, padx=10)

button_frame = tk.Frame(root, bg="#2C2F33")
button_frame.pack()

execute_btn = tk.Button(button_frame, text="Execute", command=execute_script, bg="#7289DA", fg="white", width=10)
execute_btn.grid(row=0, column=0, padx=5, pady=5)

clear_btn = tk.Button(button_frame, text="Clear", command=clear_script, bg="#99AAB5", fg="black", width=10)
clear_btn.grid(row=0, column=1, padx=5, pady=5)

open_btn = tk.Button(button_frame, text="Open File", command=open_file, bg="#99AAB5", fg="black", width=10)
open_btn.grid(row=0, column=2, padx=5, pady=5)

inject_btn = tk.Button(button_frame, text="Inject", command=inject, bg="#43B581", fg="white", width=10)
inject_btn.grid(row=0, column=3, padx=5, pady=5)

update_file_list(os.getcwd())

root.mainloop()