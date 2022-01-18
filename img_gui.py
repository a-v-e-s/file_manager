import tkinter as tk
from tkinter.filedialog import askdirectory
from functools import partial

import utils


class Gui():

    def __init__(self):
        
        # state information:
        self.radio_row = 1
        self.radio_col = 1
        self.destinations = list()
        self.coroutine = None
        
        # Create the GUI for the file sorter
        root = tk.Tk()
        root.title('Image Sorter')
    
    
        add_sorts = tk.LabelFrame(master=root, text='Add Source Directory:')
        # new directory to sort:
        to_sort = tk.Entry(master=add_sorts, width=96, bg='white', fg='black')
        to_sort.grid(row=1, column=1)
        # find new directory to sort
        browse_sort = tk.Button(
            master=add_sorts,
            text='Browse:',
            command=lambda x=to_sort: [
                x.delete(0, len(x.get())),
                x.insert(0, askdirectory()),
            ]
        )
        browse_sort.grid(row=1, column=2)
        #
        add_sorts.grid(row=1)
    
    
        sort_texts = tk.LabelFrame(master=root, text='Source Directories:')
        # directories to fully sort:
        self.fully_sorted = tk.Text(master=sort_texts, width=48, height=6, bg='white', fg='black')
        full_add = tk.Button(
            master=sort_texts,
            text='Add to Fully Sorted',
            command=lambda x=to_sort, y=self.fully_sorted: [
                y.insert('1.0', f'{x.get()}\n'),
                x.delete(0, len(x.get())),
            ]
        )
        full_add.grid(row=1, column=1)
        self.fully_sorted.grid(row=2, column=1)
        # directories to partially sort based on filetype
        self.filter_sorted = tk.Text(master=sort_texts, width=48, height=6, bg='white', fg='black')
        filter_add = tk.Button(
            master=sort_texts,
            text='Add to Filter & Sort',
            command=lambda x=to_sort, y=self.filter_sorted: [
                y.insert('1.0', f'{x.get()}\n'),
                x.delete(0, len(x.get())),
            ]
        )
        filter_add.grid(row=1, column=2)
        self.filter_sorted.grid(row=2, column=2)
        # filetypes to filter for:
        tk.Label(master=sort_texts, text='Filtered Filetypes:').grid(row=1, column=3)
        self.filetypes = tk.Text(master=sort_texts, width=12, height=6, bg='white', fg='black')
        self.filetypes.grid(row=2, column=3)
        #
        sort_texts.grid(row=2)
    
    
        main_btns = tk.Frame(master=root)
        # Run the main program loop:
        begin = tk.Button(
            master=main_btns,
            text='Begin Sorting!',
            command=self.sorting_coroutine
        )
        begin.grid(row=1, column=1)
        # Close the Application:
        quit_ = tk.Button(
            master=main_btns,
            text='Quit!',
            command=root.destroy
        )
        quit_.grid(row=1, column=2)
        #
        main_btns.grid(row=3)
    
    
        create_dest = tk.LabelFrame(master=root, text='Add Destination Directory:')
        self.dest = tk.StringVar()
        #
        self.new_dest = tk.Entry(master=create_dest, width=84, bg='white', fg='black')
        self.new_dest.grid(row=1, column=1)
        # Find a destination:
        dest_browse = tk.Button(
            master=create_dest,
            text='Browse',
            command=lambda x=self.new_dest: [
                x.delete(0, len(x.get())),
                x.insert(0, askdirectory()),
            ]
        )
        dest_browse.grid(row=1, column=2)
        # Add to possible destinations:
        add_dest = tk.Button(
            master=create_dest,
            text='Add!',
            command=self.add_radio_btn
        )
        add_dest.grid(row=1, column=3)
        #
        create_dest.grid(row=4)
    
    
        # radio buttons for destination directories:
        self.radio_frm = tk.LabelFrame(root, text='Destinations:')
        self.radio_frm.grid(row=5)
    
    
        final_btns = tk.Frame(master=root)
        # copy file to a destination
        move = tk.Button(
            master=final_btns,
            text='Copy',
            command=self.send
        )
        move.grid(row=1, column=1)
        # skip this file:
        skip = tk.Button(
            master=final_btns,
            text='Skip',
            command=self.skip
        )
        skip.grid(row=1, column=2)
        # 
        final_btns.grid(row=6)


        # Frame for sending error and other messages to the user:
        msgs = tk.LabelFrame(master=root, text='Errors:')
        #
        self.msg = tk.Label(master=msgs, width=96, fg='red')
        self.msg.grid(row=1)
        #
        msgs.grid(row=7)
    
        # Run it!
        root.mainloop()


    def add_radio_btn(self):
        """ Put a new radio button option in the radio button frame """
        
        if self.radio_row >= 21:
            msg = 'Too many radio buttons!'
            self.message(msg)
            raise OverflowError(msg)
        
        destination = self.new_dest.get()
        if destination in self.destinations:
            msg = f'{destination} already chosen!'
            self.message(msg)
            raise RuntimeError(msg)
        self.destinations.append(destination)

        # create and place the button and label:
        lbl_text = self.new_dest.get()
        radio_btn = tk.Radiobutton(master=self.radio_frm, value=lbl_text, variable=self.dest)
        radio_btn.grid(row=self.radio_row, column=self.radio_col)
        radio_btn.deselect()
        lbl = tk.Label(master=self.radio_frm, text=lbl_text)
        lbl.grid(row=self.radio_row, column=self.radio_col+1)
        
        # increment values for columns and rows:
        if self.radio_col > 3:
            self.radio_col = 1
            self.radio_row += 1
        else:
            self.radio_col += 2


    def message(self, msg):
        """ Tell the user something """

        self.msg.config(text=msg)


    def sorting_coroutine(self):
        """ Initialize the file sorting coroutine """

        full_dirs = [line for line in self.fully_sorted.get('1.0', 'end-1c').splitlines() if line != '']
        filter_dirs = [line for line in self.filter_sorted.get('1.0', 'end-1c').splitlines() if line != '']
        filter_filetypes = [line for line in self.filetypes.get('1.0', 'end-1c').splitlines() if line != '']

        print(f'full_dirs: {full_dirs}')
        print(f'filter_dirs: {filter_dirs}')
        print(f'filter_filetypes: {filter_filetypes}')

        #self.coroutine = utils.sorting_coroutine(full_dirs, filter_dirs, filter_filetypes)
        #self.coroutine.send(None)


    def send(self):
        """ Send a value to the coroutine """

        print(f'sending: {self.dest.get()}')
        #self.coroutine.send(self.dest.get())


    def skip(self):
        """ Tell the coroutine to skip the current file """

        print('Sending None!')
        #self.coroutine.send(None)


if __name__ == '__main__':
    Gui()