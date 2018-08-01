import pandas as pd
import cycluster as cy
import os.path as op
import numpy as np
import palettable
from custom_legends import colorLegend
import seaborn as sns
from hclusterplot import *
import matplotlib.pyplot as plt
import pprint
import openpyxl
from plotnine import *
# import preprocessing as prep
import scipy.cluster.hierarchy as sch
from matplotlib import cm
from matplotlib.gridspec import GridSpec
import sklearn
import matplotlib as mpl
import itertools
from scipy.spatial import distance
import os
import plotting as plot
import matplotlib.patches as mpatches
from texttable import Texttable
from tkinter import *
from tkinter.filedialog import askopenfilename
import pandas as pd
from PIL import ImageTk
import threading
import queue


class App(Frame):
    data = pd.DataFrame().fillna(0)
    index = []
    drop_columns = []
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.upload_button()
        self.title()
        w = master.winfo_screenwidth()
        h = master.winfo_screenheight()
        self.master.geometry("%dx%d+0+0" % (w - 50, h - 120))

    def process_queue(self):
        try:
            self.data = self.queue.get(0)
            self.display_button()
            self.close_title()
        except Queue.empty:
            self.master.after(100, self.process_queue)

    def title(self):
        img = ImageTk.PhotoImage(file=('Cycluster_Logo.PNG'))
        self.tit = Label()
        self.tit.config(image=img)
        self.tit.image = img
        self.tit.grid(row=1)
        self.tit.grid_rowconfigure(1,weight=1)

    def upload_button(self):
        self.upload = Button(self)
        self.upload['text'] = 'Upload File'
        self.upload['bg'] = 'red'
        self.upload['command'] = combine_funcs(self.start_file_upload)
        width, height = self.master.winfo_screenwidth(), self.master.winfo_screenheight()
        self.upload.grid(row=0, padx=(width - 50)/2,pady=(height - 120)/4)

    def start_file_upload(self):
        self.queue = queue.Queue()
        ThreadedTask(self.queue).start()
        self.master.after(100, self.process_queue)

    def close_title(self):
        self.close_tit = self.tit.grid_forget()

    def upload_button_delete(self):
        self.upload.grid_forget()

    def display_button(self):
        self.display = Button(self)
        self.display['text'] = 'Display Data'
        self.display['bg'] = 'yellow'
        self.display['command'] = combine_funcs(self.display_data, self.clear_button, self.button_delete,
                                                self.upload_button_delete, self.select_sample_button,
                                                self.drop_cols_button)
        self.display.grid()

    def button_delete(self):
        self.display.grid_forget()

    def display_data(self):
        self.data_display = Text(self)
        self.data_display.insert('0.0',self.data)
        self.data_display.grid(row=0,column=0)
        self.scrollbr = Scrollbar(command=self.data_display.yview)
        self.data_display['yscrollcommand'] = self.scrollbr.set
        self.scrollbr.grid(row=0,column=1,sticky="ns")

    def clear_button(self):
        self.close = Button(self)
        self.close['text'] = 'Clear'
        self.close['bg'] = 'yellow'
        self.close['command'] = combine_funcs(self.close_data, self.display_button, self.close_close_button,
                                              self.upload_button, self.remove_sample_selection, self.col_button_close)
        self.close.grid(row=1)

    def close_data(self):
        self.data_display.grid_forget()
        self.scrollbr.grid_forget()

    def close_close_button(self):
        self.close.grid_forget()

    def select_sample_button(self):
        self.ssb = Button(self)
        self.ssb['text'] = 'Select Sample'
        self.ssb['bg'] = 'red'
        self.ssb['command'] = self.select_sample
        self.ssb.grid(row=2)

    def select_sample(self):
        self.window = Toplevel(self, width=500, height=300)
        options = self.data.columns.values
        self.variable = StringVar(self.window)
        self.variable.set(options[0])
        self.ddlist = OptionMenu(self.window, self.variable, *options)
        self.ddlist.grid(row=1)
        self.selection = Label(self.window)
        self.selection['text'] = 'Please Select the Sample Column'
        self.selection['bg'] = 'yellow'
        self.selection.grid(row=0)
        self.done = Button(self.window)
        self.done['text'] = 'Done'
        self.done['bg'] = "green"
        self.done['command'] = combine_funcs(self.close_selection_window, self.get_sample)
        self.done.grid(row=2)


    def close_selection_window(self):
        self.window.destroy()

    # def close_ddlist(self):
    #     self.ddlist.grid_forget()

    # def next_button_1(self):
    #     self.next_1 = Button(self)
    #     self.next_1['text'] = 'Select Sample Column:'
    #     self.next_1['bg'] = 'green'
    #     self.next_1['command'] = combine_funcs(self.get_sample, self.remove_sample_selection, self.close_ddlist,
    #                                            self.drop_cols)
    #     self.next_1.grid(row=2)

    def get_sample(self):
        self.index = self.variable.get()

    def remove_sample_selection(self):
        self.ssb.grid_forget()

    def drop_cols_button(self):
        self.drop_button = Button(self)
        self.drop_button['text'] = 'Drop Columns'
        self.drop_button['bg'] = 'red'
        self.drop_button['command'] = self.drop_cols
        self.drop_button.grid(row=2, column=1)

    def col_button_close(self):
        self.drop_button.grid_forget()

    def drop_cols(self):
        self.drop_window = Toplevel(self, width=500, height=300)
        self.drop_variable = StringVar()
        for choice in self.data.columns.values:
            self.drop = Radiobutton(self.drop_window, text=choice, value=choice, variable=self.drop_variable)
        self.drop.grid(row=0, column=0)
        # self.drop['yscrollcommand'] = self.box_scrollbr.set
        # self.box_scrollbr.grid(row=0, column=1,sticky='ns')

    # def add_drop(self):
    #     for choice, value in self.choices.items():
    #         if value == 1:
    #             if choice not in self.drop_columns:
    #                 self.drop_columns += [choice]
    #             else:
    #                 continue


class ThreadedTask(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.upload_file()
    def upload_file(self):
        self.file = askopenfilename(title="Choose a file!",
                               filetypes=[('CSV File', '*.csv')])
        try:
            self.usefile = open(self.file, "r")
            self.queue.put(pd.read_csv(self.usefile))
        except:
            print("File does not exist!")






def combine_funcs(*funcs):
    def combined_func(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)
    return combined_func





app = App(master=Tk())
app.master.title("Cycluster")
app.mainloop()
print(app.index)

