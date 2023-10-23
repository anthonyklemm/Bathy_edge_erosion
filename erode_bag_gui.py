import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from erode_bag_functions import process_bag
import os
import time


def browse_input_bag():
    input_bag = filedialog.askopenfilename(filetypes=[("BAG files", "*.bag")])
    input_bag_var.set(input_bag)

def browse_output_dir():
    output_dir = filedialog.askdirectory()
    output_dir_var.set(output_dir)
    
def process():
    start_time = time.time()
    print('***commencing erosion process***')
    print('***NOTE: disregard warnings about cornerPoints or SingleCRS***')
    input_bag = input_bag_var.get()
    output_dir = output_dir_var.get()
    process_bag(input_bag, output_dir, progress, root)
    status_label['text'] = "Processing completed successfully!"
    print("***Processing completed successfully!***")
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"The function took {execution_time:.2f} seconds to run.")
    os.startfile(output_dir)

def create_widgets(root):
    tk.Label(root, text="Input BAG file:").grid(row=0, column=0, sticky="e")
    tk.Entry(root, textvariable=input_bag_var, width=40).grid(row=0, column=1)
    tk.Button(root, text="Browse", command=browse_input_bag).grid(row=0, column=2)

    tk.Label(root, text="Output directory:").grid(row=1, column=0, sticky="e")
    tk.Entry(root, textvariable=output_dir_var, width=40).grid(row=1, column=1)
    tk.Button(root, text="Browse", command=browse_output_dir).grid(row=1, column=2)

    tk.Button(root, text="Process", command=process).grid(row=2, column=1, pady=10)

    progress_label = tk.Label(root, text="Progress:")
    progress_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")

    progress = ttk.Progressbar(root, orient="horizontal", length=200, mode='determinate')
    progress.grid(row=3, column=1, padx=10, pady=10, sticky="w")
    progress["maximum"] = 100
    progress["value"] = 0

    status_label = tk.Label(root, text="")
    status_label.grid(row=4, column=1, padx=10, pady=10)

    return progress, status_label

root = tk.Tk()
root.title("Erode BAG GUI")

input_bag_var = tk.StringVar()
output_dir_var = tk.StringVar()

progress, status_label = create_widgets(root)

root.mainloop()
