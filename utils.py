""" 
Utility functions
Author: Jon David Tannehill
"""


import os
import pickle
import hashlib
import subprocess
import time
from tempfile import TemporaryDirectory
from shutil import copy2
# jank to avoid deprecation warnings:
from setuptools import distutils; from distutils.dir_util import copy_tree

import psutil
import PIL


HOME = os.getenv('HOME')

with open('managed.txt', 'r') as file:
    MANAGED = {f'{HOME}/{line.strip()}' for line in file.readlines()}

with open('ignored.txt', 'r') as file:
    IGNORED = {line.strip() for line in file.readlines()}



class FiletypeError(Exception):
    pass


def sorting_coroutine(full_dirs, filter_dirs, filter_filetypes):
    """ File sorting coroutine """

    # get all pickles of filehashes:
    pickles = dict()
    pickles_changed = False # used later
    for dir_ in MANAGED:
        try:
            pickles[dir_] = load_pickle(dir_)
        except FileNotFoundError:
            pickles[dir_] = generate_pickle(dir_)

    
    # create a temporary directory,
    with TemporaryDirectory() as tdir:
        
        # then move all the stuff to it for sorting:
        for dir_ in full_dirs:
            copy_tree(dir_, tdir)
        #
        for dir_ in filter_dirs:
            
            for filetype in filetypes:
                p = subprocess.Popen(
                    ['find', dir_, '-type', 'f', '-iname', f'*{filetype}'],
                    stdout=subprocess.PIPE
                )
                
                for file_ in str(p.stdout.read()).split('\\n'):
                    try:
                        copy2(file_.lstrip("b'"), tdir)
                    except FileNotFoundError:
                        pass

        # the main loop!
        for root, _, fns in os.walk(tdir):
            #
            for fn in fns:
                #
                filepath = os.path.join(root, fn)
                filehash = get_hash(filepath)
                
                # display the file for the user:
                displaying = False
                if fn[-3:] in {jpg, png, bmp, gif, peg, ebp}:
                    try:
                        display_img(fn)
                        displaying = True
                    except PIL.UnidentifiedImageError:
                        subprocess.Popen(['xdg-open', fn], stdout=subprocess.PIPE)
                #
                else:
                    p = subprocess.Popen(['xdg-open', fn], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    err = p.stderr.read()
                    if err:
                        #raise FiletypeError() # this would break coroutine
                        print(f'xdg-open failed with {fn}:\n{err}.')
                        print('\nContinuing...')
                        continue

                # Wait patiently here for destination directory
                destination = (yield)
                if displaying: close_display()

                if destination is None:
                    continue
                
                # do we track files in this files destination?
                if (predestination := '/'+'/'.join(destination.split('/')[1:4])) in MANAGED:

                    # does it already exist?
                    if filehash in pickles[predestination]:
                        #raise FileExistsError() # this would break coroutine
                        print(f'{fn} found in {destination}:\n\t{pickles[predestination][filehash]}')
                        print('Continuing...')
                        continue

                    # if not, track it:
                    else:
                        copy2(fn, destination)
                        pickles[predestination][filehash] = os.path.join(destination, fn)
                        if not pickles_changed: # they've changed now!
                            pickles_changed = [predestination]
                        elif predestination not in pickles_changed:
                            pickles_changed.append(predestination)

                # just stick it in there.
                else: copy2(fn, destination)

        # update our pickles:
        if pickles_changed:
            for pkl in pickles_changed:
                with open(os.path.join(pkl, 'file_db.pkl'), 'rb') as file:
                    pickle.dump(pickles[pkl], file)


def get_hash(filename, alg=hashlib.sha1):
    """ Return hexdigest of a given file's hash """

    hash_ = alg()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            hash_.update(data)
    
    return hash_.hexdigest()


def display_img(fn):
    """ Display an image for the user. """
    
    with PIL.Image.open(fn) as img:
        img.show()


def close_display():
    """ Close the display of the image. """

    for ps in psutil.process_iter():
        if ps.name() == 'display':
            ps.kill()
            break


def load_pickle(folder):
    """ Load dictionaries from pickle files in managed folders """

    filename = f'{folder}/file_db.pkl'
    if os.path.isfile(filename):
        dic = pickle.load(filename)
    else:
        raise FileNotFoundError

    return dic


def generate_pickle(folder, recursive=True, save=True):
    """ Create a pickle file with a dictionary of filehashes and relative paths """
    
    dic = dict()
    
    if recursive:
        for root, _, files in os.walk(folder):
            if not os.path.split(root)[-1] in IGNORED:
    
                for file in files:
                    filename = os.path.join(root, file)
    
                    if os.path.isfile(filename):
                        filehash = get_hash(filename)
                        relpath = filename.lstrip(f'{folder}/')
                        dic[filehash] = relpath
    
    else:
        for file in os.listdir(folder):
            filename = os.path.join(folder, file)
            
            if os.path.isfile(filename):
                filehash = get_hash(filename)
                relpath = filename.lstrip(f'{folder}/')
                dic[filehash] = relpath

    
    if save:
        with open(f'{folder}/file_db.pkl', 'wb') as f:
            pickle.dump(dic, f)

    return dic


if __name__ == '__main__':
    pass