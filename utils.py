""" 
Utility functions for file_maanger package

Author: Jon David Tannehill
"""


import os
import pickle
import hashlib

import psutil
from PIL import Image


HOME = os.getenv('HOME')

with open('managed.txt', 'r') as file:
    MANAGED = {f'{HOME}/{line.strip()}' for line in file.readlines()}

with open('ignored.txt', 'r') as file:
    IGNORED = {line.strip() for line in file.readlines()}


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
    
    with Image.open(fn) as img:
        img.thumbnail((720, 720))
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
        with open(filename, 'rb') as file:
            dic = pickle.load(file)
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