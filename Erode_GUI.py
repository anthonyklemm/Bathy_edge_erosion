# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 16:22:41 2023

@author: Anthony.R.Klemm
"""
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from erode_bag_functions import process_bag
from erode_csar_functions import erode_outer_edge  # Import the CSAR erosion function
from erode_geotiff_functions import process_geotiff  # Import the GeoTIFF erosion function
import os
import time
import threading
import sys


class CustomStream:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.yview(tk.END)

    def flush(self):
        pass


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Erode File GUI")

        self.input_file_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.file_format_var = tk.StringVar(value="CSAR")  # Default value
        #self.file_format_var = tk.StringVar(value="GeoTiff")  # Default value changed to GeoTIFF


        self.create_widgets()

    def browse_input_file(self):
        file_format = self.file_format_var.get()
        if file_format == "BAG":
            filetypes = [("BAG files", "*.bag")]
        elif file_format == "CSAR":
            filetypes = [("CSAR files", "*.csar")]
        else:
            filetypes = [("GeoTIFF files", "*.tif;*.tiff")]
        input_file = filedialog.askopenfilename(filetypes=filetypes)
        self.input_file_var.set(input_file)


    def browse_output_dir(self):
        output_dir = filedialog.askdirectory()
        self.output_dir_var.set(output_dir)

    def process(self):
        self.progress["value"] = 0
        threading.Thread(target=self._process, daemon=True).start()

    def _process(self):
        start_time = time.time()
        self.add_message('***commencing erosion process***')

        file_format = self.file_format_var.get()
        input_file = self.input_file_var.get()
        output_dir = self.output_dir_var.get()

        if not input_file or not output_dir:
            self.add_message("Please select an input file and output directory.")
            return

        original_stdout = sys.stdout
        sys.stdout = CustomStream(self.message_text)

        try:
            if file_format == "BAG":
                process_bag(input_file, output_dir, self.progress, self.root)
            elif file_format == "GeoTiff":
                process_geotiff(input_file, output_dir, self.progress, self.root)
            elif file_format == "CSAR":
                root, ext = os.path.splitext(os.path.basename(input_file))
                eroded_csar = os.path.join(output_dir, f"{root}_eroded.csar")
                erode_outer_edge(input_file, eroded_csar, progress=self.progress)

        finally:
            sys.stdout = original_stdout

        self.status_label['text'] = "Processing completed successfully. Have a Happy Hydro Day!"
        self.add_message("***Processing completed successfully. Have a Happy Hydro Day!***")

        end_time = time.time()
        execution_time = end_time - start_time
        self.add_message(f"The function took {execution_time:.2f} seconds to run.")
        os.startfile(output_dir)

        self.progress["value"] = 100

    def add_message(self, message):
        self.message_text.insert(tk.END, message + '\n')
        self.message_text.yview(tk.END)

    def create_widgets(self):
        tk.Label(self.root, text="Input file:").grid(row=0, column=0, sticky="e")
        tk.Entry(self.root, textvariable=self.input_file_var, width=40).grid(row=0, column=1)
        tk.Button(self.root, text="Browse", command=self.browse_input_file).grid(row=0, column=2)

        tk.Label(self.root, text="Output directory:").grid(row=1, column=0, sticky="e")
        tk.Entry(self.root, textvariable=self.output_dir_var, width=40).grid(row=1, column=1)
        tk.Button(self.root, text="Browse", command=self.browse_output_dir).grid(row=1, column=2)

        tk.Label(self.root, text="Choose File format:").grid(row=2, column=0, sticky="e")
        tk.OptionMenu(self.root, self.file_format_var, "BAG", "CSAR", 'GeoTiff').grid(row=2, column=1)

        tk.Button(self.root, text="Process", command=self.process).grid(row=3, column=1, pady=10)

        self.progress_label = tk.Label(self.root, text="Progress:")
        self.progress_label.grid(row=4, column=0, padx=10, pady=10, sticky="e")

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=200, mode='determinate')
        self.progress.grid(row=4, column=1, padx=10, pady=10, sticky="w")
        self.progress["maximum"] = 100
        self.progress["value"] = 0

        self.status_label = tk.Label(self.root, text="")
        self.status_label.grid(row=5, column=1, padx=10, pady=10)

        self.message_text = tk.Text(self.root, wrap='word', height=10, width=80)
        self.message_text.grid(row=6, column=0, columnspan=3, padx=10, pady=10)
        
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construct the path to the image
        image_path = os.path.join(current_dir, 'image.png')
        
        # Load image or GIF
        self.image = tk.PhotoImage(file=image_path)
        self.image_label = tk.Label(self.root, image=self.image)
        self.image_label.grid(row=7, column=0, columnspan=3, sticky='nsew')


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
