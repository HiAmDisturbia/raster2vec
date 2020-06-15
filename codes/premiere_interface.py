# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image

root = tk.Tk()

def browse_file():
    global img
    subpath = tk.Toplevel()
    
    root.filename = filedialog.askopenfilename(initialdir = "/", title = "Select A File", filetypes = (("Image jpg files", "*.jpg"), ("Image png files", "*.png"), ("All files", "*.*")))
    path = root.filename
    label1 = tk.Label(subpath, text="File location: " + path).pack()
    img = ImageTk.PhotoImage(Image.open(path))
    label2 = tk.Label(subpath, image=img).pack()
    
def when_clicked():
    some_text = tk.Label(root, text="Value was sent to the NASA")
    some_text.pack()

canvas = tk.Canvas(root, width = 200, height = 200)
canvas.pack()

window_main = tk.Label(root, text="Billy opens files\nfor you (:")
window_main.config(font=("Serpentine", 12))
canvas.create_window(100, 50, window=window_main)

entry = tk.Entry(root)
canvas.create_window(100, 100, window=entry)

za_button = tk.Button(root, text="Input value", command=when_clicked)
canvas.create_window(100, 125, window=za_button)

za_button2 = tk.Button(root, text="Browse file", command=browse_file)
canvas.create_window(100, 150, window=za_button2)

root.mainloop()