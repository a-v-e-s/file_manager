#!/usr/bin/env python3

"""
Finds if a file already exists within a directory

"""


import os
from functools import partial
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename

import utils


def duplicate_checker(filename, directory, msg_frame=None):

    if type(filename) != str:
        filename = filename.get()
    if type(directory) != str:
        directory = directory.get()

    filehash = utils.get_hash(filename)

    if (predestination := '/'+'/'.join(directory.split('/')[1:4])) in utils.MANAGED:
        hashes = utils.load_pickle(predestination)
    else:
        hashes = utils.generate_pickle(directory, True, False)

    if filehash in hashes:
        if msg_frame:
            msg_frame.configure(text='Exists!')
        else:
            return True
    else:
        if msg_frame:
            msg_frame.configure(text='Not Found!')
        else:
            return False


class Gui():
    def __init__(self):

        root = tk.Tk()
        root.title('Duplicate Checker')

        file_frame = tk.LabelFrame(master=root, text='Filename:')
        self.filename = tk.Entry(master=file_frame, width=84, bg='white', fg='black')
        self.filename.grid(row=1, column=1)
        tk.Button(
            master=file_frame,
            text='Browse',
            command=lambda x=self.filename: [
                x.delete(0, len(x.get())),
                x.insert(0, askopenfilename()),
            ]
        ).grid(row=1, column=2)
        file_frame.grid(row=1, column=1, columnspan=2)

        folder_frame = tk.LabelFrame(master=root, text='Folder:')
        self.directory = tk.Entry(master=folder_frame, width=84, bg='white', fg='black')
        self.directory.grid(row=1, column=1)
        tk.Button(
            master=folder_frame,
            text='Browse',
            command=lambda x=self.directory: [
                x.delete(0, len(x.get())),
                x.insert(0, askdirectory()),
            ]
        ).grid(row=1, column=2)
        folder_frame.grid(row=2, column=1, columnspan=2)

        msg_lbl = tk.Label(master=root, fg='red')
        msg_lbl.grid(row=3, column=1, columnspan=2)

        tk.Button(
            master=root,
            text='Check!', 
            command=partial(duplicate_checker, self.filename, self.directory, msg_lbl)
        ).grid(row=4, column=1)
        tk.Button(master=root, text='Quit', command=root.destroy).grid(row=4, column=2)

        root.mainloop()


if __name__ == '__main__':
    Gui()