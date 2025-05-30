# This script creates a Tkinter GUI app that downloads the King James Bible text from Project Gutenberg, displays it in a scrollable text box, and uses pyttsx3 text-to-speech to read it aloud in chunks, with buttons to start and stop reading and a status label showing progress.

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import pyttsx3
import requests

class BibleReader:
    def __init__(self, root):
        self.root = root
        self.root.title("KJV Bible TTS Reader")

        self.text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=25)
        self.text_box.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        self.play_btn = ttk.Button(root, text="Play Bible", command=self.play_bible)
        self.play_btn.grid(row=1, column=0, padx=10, pady=5, sticky='ew')

        self.stop_btn = ttk.Button(root, text="Stop", command=self.stop_reading)
        self.stop_btn.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

        self.status_label = ttk.Label(root, text="Status: Ready")
        self.status_label.grid(row=1, column=2, padx=10, pady=5)

        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.stop_flag = False

        threading.Thread(target=self.load_bible_text, daemon=True).start()

    def load_bible_text(self):
        self.status_label.config(text="Status: Downloading Bible...")
        url = "https://www.gutenberg.org/files/10/10-0.txt"
        response = requests.get(url)
        full_text = response.text

        # Strip preface and index, start at Genesis
        start_marker = "The First Book of Moses: Called Genesis"
        end_marker = "End of the Project Gutenberg EBook of The King James Bible"

        start_index = full_text.find(start_marker)
        end_index = full_text.find(end_marker)

        self.bible_text = full_text[start_index:end_index].strip()

        # Display the full Bible text in the text box (starting at Genesis)
        self.text_box.delete(1.0, tk.END)
        self.text_box.insert(tk.END, self.bible_text)
        self.status_label.config(text="Status: Bible Loaded")


    def play_bible(self):
        self.stop_flag = False
        self.status_label.config(text="Status: Reading...")
        threading.Thread(target=self.read_bible_text, daemon=True).start()

    def read_bible_text(self):
        words = self.bible_text.split()
        chunk_size = 200  # words per chunk
        for i in range(0, len(words), chunk_size):
            if self.stop_flag:
                self.status_label.config(text="Status: Stopped")
                break
            chunk = " ".join(words[i:i+chunk_size])
            self.engine.say(chunk)
            self.engine.runAndWait()
        else:
            self.status_label.config(text="Status: Finished Reading")

    def stop_reading(self):
        self.stop_flag = True
        self.engine.stop()
        self.status_label.config(text="Status: Stopping...")

if __name__ == "__main__":
    root = tk.Tk()
    app = BibleReader(root)
    root.mainloop()
